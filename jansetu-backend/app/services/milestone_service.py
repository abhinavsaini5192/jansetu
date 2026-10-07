from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.attachment import Attachment
from app.models.deliverable import Deliverable
from app.models.milestone import Milestone
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.project_team_member import ProjectTeamMember
from app.models.user import User
from app.schemas.milestone import (
    DeliverableCreate,
    DeliverableResponse,
    DeliverableReviewRequest,
    DeliverableUpdate,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneStatusUpdate,
    MilestoneUpdate,
)
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.services.project_activity_service import project_activity_service
from app.utils.enums import (
    AuditAction,
    DeliverableStatus,
    MilestoneStatus,
    NotificationType,
    OrganizationMembershipRole,
    ProjectActivityType,
    UserRole,
)


class MilestoneService:
    """
    Milestone & Deliverables Management Service.
    Tracks project phases, deliverable submissions linking existing attachments,
    and automatic overall project progress recalculation.
    """

    def _verify_milestone_editor(self, db: Session, project: Project, current_user: User) -> None:
        """Ensures user belongs to university team, is project creator, or platform admin."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if project.created_by_user_id == current_user.id:
            return

        # University Admin
        uni_m = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if uni_m or current_user.role == UserRole.UNIVERSITY_ADMIN:
            return

        # Team member of any team under this project
        team_m = (
            db.query(ProjectTeamMember)
            .join(ProjectTeam)
            .filter(
                ProjectTeam.project_id == project.id,
                ProjectTeamMember.user_id == current_user.id,
                ProjectTeamMember.is_active == True,
            )
            .first()
        )
        if team_m:
            return

        raise ForbiddenException("Only authorized project members can manage milestones.")

    def _recalculate_project_progress(self, db: Session, project_id: str) -> int:
        """Recalculates overall project execution progress from average milestone completion."""
        milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
        if not milestones:
            return 0
        total_pct = sum(m.completion_percentage for m in milestones)
        avg_pct = round(total_pct / len(milestones))
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.progress_percentage = avg_pct
            db.flush()
        return avg_pct

    def create_milestone(
        self,
        db: Session,
        project_id: str,
        req: MilestoneCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Milestone:
        """Creates a new project execution milestone."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        self._verify_milestone_editor(db, project, current_user)

        if req.completion_percentage < 0 or req.completion_percentage > 100:
            raise BadRequestException("Completion percentage must be between 0 and 100.")

        milestone = Milestone(
            project_id=project_id,
            title=req.title,
            description=req.description,
            sequence_number=req.sequence_number,
            planned_start_date=req.planned_start_date,
            planned_end_date=req.planned_end_date,
            completion_percentage=req.completion_percentage,
            status=MilestoneStatus.NOT_STARTED if req.completion_percentage == 0 else MilestoneStatus.IN_PROGRESS,
            created_by_user_id=current_user.id,
        )
        db.add(milestone)
        db.flush()
        self._recalculate_project_progress(db, project_id)
        db.commit()
        db.refresh(milestone)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="milestone",
            entity_id=milestone.id,
            description=f"Created milestone '{milestone.title}' (#{milestone.sequence_number}) for project '{project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=project_id,
            activity_type=ProjectActivityType.MILESTONE_CREATED,
            title="Milestone Defined",
            description=f"Milestone #{milestone.sequence_number} '{milestone.title}' added to roadmap",
            actor_user_id=current_user.id,
            related_entity_type="milestone",
            related_entity_id=milestone.id,
        )

        return milestone

    def list_milestones(self, db: Session, project_id: str, current_user: User) -> List[Milestone]:
        """Lists milestones ordered by sequence number."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not project_activity_service.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to view this project's milestones.")

        return (
            db.query(Milestone)
            .options(joinedload(Milestone.deliverables))
            .filter(Milestone.project_id == project_id)
            .order_by(Milestone.sequence_number.asc())
            .all()
        )

    def get_milestone(self, db: Session, milestone_id: str, current_user: User) -> Milestone:
        """Retrieves a milestone by ID."""
        milestone = (
            db.query(Milestone)
            .options(joinedload(Milestone.deliverables), joinedload(Milestone.project))
            .filter(Milestone.id == milestone_id)
            .first()
        )
        if not milestone:
            raise NotFoundException(f"Milestone '{milestone_id}' not found.")

        if not project_activity_service.check_project_access(db, milestone.project, current_user):
            raise ForbiddenException("You do not have permission to view this milestone.")

        return milestone

    def update_milestone(
        self,
        db: Session,
        milestone_id: str,
        req: MilestoneUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Milestone:
        """Updates milestone progress, timeline, or status."""
        milestone = self.get_milestone(db, milestone_id, current_user)
        self._verify_milestone_editor(db, milestone.project, current_user)

        pct = req.completion_percentage if req.completion_percentage is not None else req.progress
        if pct is not None:
            if pct < 0 or pct > 100:
                raise BadRequestException("Completion percentage must be between 0 and 100.")
            milestone.completion_percentage = pct

        if req.title is not None:
            milestone.title = req.title
        if req.description is not None:
            milestone.description = req.description
        if req.sequence_number is not None:
            milestone.sequence_number = req.sequence_number
        if req.planned_start_date is not None:
            milestone.planned_start_date = req.planned_start_date
        if req.planned_end_date is not None:
            milestone.planned_end_date = req.planned_end_date
        if req.actual_start_date is not None:
            milestone.actual_start_date = req.actual_start_date
        if req.actual_end_date is not None:
            milestone.actual_end_date = req.actual_end_date

        if req.status is not None:
            milestone.status = req.status
            if req.status == MilestoneStatus.COMPLETED:
                milestone.completion_percentage = 100
                if not milestone.actual_end_date:
                    milestone.actual_end_date = datetime.now(timezone.utc)

        milestone.updated_at = datetime.now(timezone.utc)
        db.flush()
        self._recalculate_project_progress(db, milestone.project_id)
        db.commit()
        db.refresh(milestone)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="milestone",
            entity_id=milestone.id,
            description=f"Updated milestone '{milestone.title}' (Status: {milestone.status.value}, Progress: {milestone.completion_percentage}%)",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=milestone.project_id,
            activity_type=ProjectActivityType.MILESTONE_UPDATED,
            title="Milestone Updated",
            description=f"Milestone '{milestone.title}' progress updated to {milestone.completion_percentage}% ({milestone.status.value})",
            actor_user_id=current_user.id,
            related_entity_type="milestone",
            related_entity_id=milestone.id,
        )

        return milestone

    def delete_milestone(
        self,
        db: Session,
        milestone_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Deletes a milestone and recalculates project progress."""
        milestone = self.get_milestone(db, milestone_id, current_user)
        self._verify_milestone_editor(db, milestone.project, current_user)

        project_id = milestone.project_id
        title = milestone.title

        db.delete(milestone)
        db.flush()
        self._recalculate_project_progress(db, project_id)
        db.commit()

        audit_service.log_event(
            db=db,
            action=AuditAction.DELETE,
            entity_type="milestone",
            entity_id=milestone_id,
            description=f"Deleted milestone '{title}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def create_deliverable(
        self,
        db: Session,
        milestone_id: str,
        req: DeliverableCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Deliverable:
        """Creates a deliverable under a milestone, optionally linking an existing attachment."""
        milestone = self.get_milestone(db, milestone_id, current_user)
        self._verify_milestone_editor(db, milestone.project, current_user)

        # Verify attachment if provided
        if req.file_attachment_id:
            att = db.query(Attachment).filter(Attachment.id == req.file_attachment_id).first()
            if not att:
                raise NotFoundException(f"Attachment '{req.file_attachment_id}' not found.")

        deliverable = Deliverable(
            milestone_id=milestone_id,
            title=req.title,
            description=req.description,
            file_attachment_id=req.file_attachment_id,
            submitted_by_user_id=current_user.id,
            status=DeliverableStatus.SUBMITTED if req.file_attachment_id else DeliverableStatus.PENDING,
            submitted_at=datetime.now(timezone.utc) if req.file_attachment_id else None,
        )
        db.add(deliverable)
        db.commit()
        db.refresh(deliverable)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="deliverable",
            entity_id=deliverable.id,
            description=f"Submitted deliverable '{deliverable.title}' for milestone '{milestone.title}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=milestone.project_id,
            activity_type=ProjectActivityType.DELIVERABLE_SUBMITTED,
            title="Deliverable Submitted",
            description=f"Deliverable '{deliverable.title}' submitted for milestone '{milestone.title}'",
            actor_user_id=current_user.id,
            related_entity_type="deliverable",
            related_entity_id=deliverable.id,
        )

        return deliverable

    def list_deliverables(self, db: Session, milestone_id: str, current_user: User) -> List[Deliverable]:
        """Lists deliverables for a milestone."""
        milestone = self.get_milestone(db, milestone_id, current_user)
        return (
            db.query(Deliverable)
            .options(joinedload(Deliverable.attachment))
            .filter(Deliverable.milestone_id == milestone_id)
            .all()
        )

    def get_deliverable(self, db: Session, deliverable_id: str, current_user: User) -> Deliverable:
        """Gets deliverable by ID."""
        deliverable = (
            db.query(Deliverable)
            .options(joinedload(Deliverable.milestone).joinedload(Milestone.project), joinedload(Deliverable.attachment))
            .filter(Deliverable.id == deliverable_id)
            .first()
        )
        if not deliverable:
            raise NotFoundException(f"Deliverable '{deliverable_id}' not found.")

        if not project_activity_service.check_project_access(db, deliverable.milestone.project, current_user):
            raise ForbiddenException("You do not have permission to view this deliverable.")

        return deliverable

    def update_deliverable(
        self,
        db: Session,
        deliverable_id: str,
        req: DeliverableUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Deliverable:
        """Updates deliverable metadata."""
        deliverable = self.get_deliverable(db, deliverable_id, current_user)
        self._verify_milestone_editor(db, deliverable.milestone.project, current_user)

        if req.title is not None:
            deliverable.title = req.title
        if req.description is not None:
            deliverable.description = req.description
        if req.file_attachment_id is not None:
            deliverable.file_attachment_id = req.file_attachment_id
            deliverable.status = DeliverableStatus.SUBMITTED
            deliverable.submitted_at = datetime.now(timezone.utc)

        deliverable.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(deliverable)

        return deliverable

    def review_deliverable(
        self,
        db: Session,
        deliverable_id: str,
        req: DeliverableReviewRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Deliverable:
        """Reviews deliverable and transitions status."""
        deliverable = self.get_deliverable(db, deliverable_id, current_user)

        # Allow Government, Platform Admin, or University Lead Faculty
        allowed_roles = (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER, UserRole.UNIVERSITY_ADMIN)
        is_lead_faculty = deliverable.milestone.project.created_by_user_id == current_user.id
        if current_user.role not in allowed_roles and not is_lead_faculty:
            raise ForbiddenException("Only project faculty mentors or government reviewers can review deliverables.")

        decision = req.decision.lower()
        if decision == "accept":
            deliverable.status = DeliverableStatus.ACCEPTED
        elif decision == "reject":
            deliverable.status = DeliverableStatus.REJECTED
        elif decision == "request_revision":
            deliverable.status = DeliverableStatus.NEEDS_REVISION
        else:
            raise BadRequestException(f"Invalid review decision '{decision}'.")

        deliverable.reviewed_at = datetime.now(timezone.utc)
        deliverable.reviewed_by_user_id = current_user.id
        if req.review_comment:
            deliverable.review_comment = req.review_comment
        deliverable.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(deliverable)

        # Audit & Activity
        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="deliverable",
            entity_id=deliverable.id,
            description=f"Reviewed deliverable '{deliverable.title}': {deliverable.status.value}",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=deliverable.milestone.project_id,
            activity_type=ProjectActivityType.DELIVERABLE_REVIEWED,
            title=f"Deliverable {deliverable.status.value.capitalize()}",
            description=f"Deliverable '{deliverable.title}' marked as {deliverable.status.value}",
            actor_user_id=current_user.id,
            related_entity_type="deliverable",
            related_entity_id=deliverable.id,
        )

        notification_service.create_notification(
            db=db,
            recipient_user_id=deliverable.submitted_by_user_id,
            notification_type=NotificationType.SYSTEM,
            title=f"Deliverable {deliverable.status.value.capitalize()}",
            message=f"Deliverable '{deliverable.title}' has been {deliverable.status.value}.",
            related_challenge_id=deliverable.milestone.project.challenge_id,
        )

        return deliverable

    def serialize_deliverable_response(self, deliverable: Deliverable) -> DeliverableResponse:
        """Serializes Deliverable ORM model to DeliverableResponse schema."""
        return DeliverableResponse(
            id=deliverable.id,
            milestone_id=deliverable.milestone_id,
            title=deliverable.title,
            description=deliverable.description,
            file_attachment_id=deliverable.file_attachment_id,
            submitted_by_user_id=deliverable.submitted_by_user_id,
            status=deliverable.status,
            submitted_at=deliverable.submitted_at,
            reviewed_at=deliverable.reviewed_at,
            reviewed_by_user_id=deliverable.reviewed_by_user_id,
            review_comment=deliverable.review_comment,
            created_at=deliverable.created_at,
            updated_at=deliverable.updated_at,
        )

    def serialize_milestone_response(self, milestone: Milestone) -> MilestoneResponse:
        """Serializes Milestone ORM model to MilestoneResponse schema with deliverables and progress."""
        deliverables = [
            self.serialize_deliverable_response(d)
            for d in (milestone.deliverables or [])
        ]
        due_str = milestone.planned_end_date.strftime("%Y-%m-%d") if milestone.planned_end_date else None
        return MilestoneResponse(
            id=milestone.id,
            project_id=milestone.project_id,
            title=milestone.title,
            description=milestone.description,
            sequence_number=milestone.sequence_number,
            planned_start_date=milestone.planned_start_date,
            planned_end_date=milestone.planned_end_date,
            actual_start_date=milestone.actual_start_date,
            actual_end_date=milestone.actual_end_date,
            status=milestone.status,
            completion_percentage=milestone.completion_percentage,
            progress=milestone.completion_percentage,
            dueDate=due_str,
            created_by_user_id=milestone.created_by_user_id,
            created_at=milestone.created_at,
            updated_at=milestone.updated_at,
            deliverables=deliverables,
        )


milestone_service = MilestoneService()
