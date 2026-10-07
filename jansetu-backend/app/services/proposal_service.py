from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.audit_log import AuditLog
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.project_team_member import ProjectTeamMember
from app.models.proposal import Proposal
from app.models.user import User
from app.schemas.proposal import ProposalCreate, ProposalHistoryItem, ProposalReviewRequest, ProposalUpdate
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.services.project_activity_service import project_activity_service
from app.utils.enums import AuditAction, NotificationType, OrganizationMembershipRole, ProjectActivityType, ProposalStatus, UserRole


class ProposalService:
    """
    Solution Proposal Management Service.
    Handles submission, revision requests, and administrative approval of university solution blueprints.
    """

    def _verify_proposal_editor(self, db: Session, project: Project, current_user: User) -> None:
        """Ensures user belongs to project's university team or is platform admin."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
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
        team_member = (
            db.query(ProjectTeamMember)
            .join(ProjectTeam)
            .filter(
                ProjectTeam.project_id == project.id,
                ProjectTeamMember.user_id == current_user.id,
                ProjectTeamMember.is_active == True,
            )
            .first()
        )
        if team_member:
            return

        if project.created_by_user_id == current_user.id:
            return

        raise ForbiddenException("Only authorized project team members can edit proposals.")

    def _verify_proposal_reviewer(self, current_user: User) -> None:
        """Only government or platform administrators can review and approve/reject proposals."""
        allowed_roles = (
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_ADMIN,
            UserRole.DISTRICT_NODAL_OFFICER,
        )
        if current_user.role not in allowed_roles:
            raise ForbiddenException("Only authorized government or platform reviewers can evaluate proposals.")

    def create_proposal(
        self,
        db: Session,
        project_id: str,
        req: ProposalCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Proposal:
        """Creates a proposal draft for a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        self._verify_proposal_editor(db, project, current_user)

        # Verify team if specified
        team_id = req.submitted_by_team_id
        if team_id:
            team = db.query(ProjectTeam).filter(ProjectTeam.id == team_id, ProjectTeam.project_id == project_id).first()
            if not team:
                raise NotFoundException(f"Team '{team_id}' does not belong to project '{project_id}'.")
        else:
            # Fallback to first team if exists
            first_team = db.query(ProjectTeam).filter(ProjectTeam.project_id == project_id).first()
            team_id = first_team.id if first_team else None

        proposal = Proposal(
            project_id=project_id,
            submitted_by_team_id=team_id,
            title=req.title,
            summary=req.summary,
            detailed_description=req.detailed_description,
            methodology=req.methodology,
            expected_outcomes=req.expected_outcomes,
            estimated_budget=req.estimated_budget,
            required_resources=req.required_resources,
            implementation_timeline=req.implementation_timeline,
            status=ProposalStatus.DRAFT,
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="proposal",
            entity_id=proposal.id,
            description=f"Created proposal '{proposal.title}' for project '{project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return proposal

    def list_proposals(self, db: Session, project_id: str, current_user: User) -> List[Proposal]:
        """Lists all proposals associated with a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not project_activity_service.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to view this project's proposals.")

        return (
            db.query(Proposal)
            .filter(Proposal.project_id == project_id)
            .order_by(desc(Proposal.created_at))
            .all()
        )

    def get_proposal(self, db: Session, proposal_id: str, current_user: User) -> Proposal:
        """Gets a proposal by ID."""
        proposal = (
            db.query(Proposal)
            .options(joinedload(Proposal.project), joinedload(Proposal.team))
            .filter(Proposal.id == proposal_id)
            .first()
        )
        if not proposal:
            raise NotFoundException(f"Proposal '{proposal_id}' not found.")

        if not project_activity_service.check_project_access(db, proposal.project, current_user):
            raise ForbiddenException("You do not have permission to view this proposal.")

        return proposal

    def update_proposal(
        self,
        db: Session,
        proposal_id: str,
        req: ProposalUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Proposal:
        """Updates proposal draft or revision."""
        proposal = self.get_proposal(db, proposal_id, current_user)
        self._verify_proposal_editor(db, proposal.project, current_user)

        if proposal.status not in (ProposalStatus.DRAFT, ProposalStatus.NEEDS_REVISION):
            raise BadRequestException(f"Cannot edit proposal in '{proposal.status.value}' status.")

        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proposal, field, value)

        proposal.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(proposal)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="proposal",
            entity_id=proposal.id,
            description=f"Updated proposal '{proposal.title}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return proposal

    def submit_proposal(
        self,
        db: Session,
        proposal_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Proposal:
        """Transitions proposal to SUBMITTED status."""
        proposal = self.get_proposal(db, proposal_id, current_user)
        self._verify_proposal_editor(db, proposal.project, current_user)

        if proposal.status not in (ProposalStatus.DRAFT, ProposalStatus.NEEDS_REVISION):
            raise BadRequestException(f"Cannot submit proposal currently in '{proposal.status.value}' status.")

        proposal.status = ProposalStatus.SUBMITTED
        proposal.submitted_at = datetime.now(timezone.utc)
        proposal.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(proposal)

        # Audit Log & Project Activity
        audit_service.log_event(
            db=db,
            action=AuditAction.SUBMIT,
            entity_type="proposal",
            entity_id=proposal.id,
            description=f"Submitted proposal '{proposal.title}' for official evaluation",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=proposal.project_id,
            activity_type=ProjectActivityType.PROPOSAL_SUBMITTED,
            title="Proposal Submitted",
            description=f"Solution proposal '{proposal.title}' submitted for review",
            actor_user_id=current_user.id,
            related_entity_type="proposal",
            related_entity_id=proposal.id,
        )

        return proposal

    def review_proposal(
        self,
        db: Session,
        proposal_id: str,
        req: ProposalReviewRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Proposal:
        """Official administrative review of a proposal."""
        proposal = self.get_proposal(db, proposal_id, current_user)
        self._verify_proposal_reviewer(current_user)

        decision = req.decision.lower()

        if decision == "approve":
            proposal.status = ProposalStatus.APPROVED
            # Update project workspace budget/summary if provided
            if proposal.estimated_budget and not proposal.project.budget:
                proposal.project.budget = proposal.estimated_budget
        elif decision == "reject":
            proposal.status = ProposalStatus.REJECTED
        elif decision == "request_revision":
            proposal.status = ProposalStatus.NEEDS_REVISION
        elif decision == "move_to_review":
            proposal.status = ProposalStatus.UNDER_REVIEW
        else:
            raise BadRequestException(f"Invalid review decision '{decision}'.")

        proposal.reviewed_at = datetime.now(timezone.utc)
        proposal.reviewed_by_user_id = current_user.id
        if req.review_comment:
            proposal.review_comment = req.review_comment
        proposal.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(proposal)

        # Audit & Activity
        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="proposal",
            entity_id=proposal.id,
            description=f"Proposal '{proposal.title}' reviewed: {proposal.status.value}",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=proposal.project_id,
            activity_type=ProjectActivityType.PROPOSAL_REVIEWED,
            title=f"Proposal {proposal.status.value.capitalize()}",
            description=f"Review decision by {current_user.full_name}: {req.review_comment or 'No remarks'}",
            actor_user_id=current_user.id,
            related_entity_type="proposal",
            related_entity_id=proposal.id,
        )

        # Notify project team creator
        notification_service.create_notification(
            db=db,
            recipient_user_id=proposal.project.created_by_user_id,
            notification_type=NotificationType.SYSTEM,
            title=f"Proposal {proposal.status.value.capitalize()}",
            message=f"Proposal '{proposal.title}' has been {proposal.status.value}. Notes: {req.review_comment or 'None'}",
            related_challenge_id=proposal.project.challenge_id,
        )

        return proposal

    def get_proposal_history(self, db: Session, proposal_id: str, current_user: User) -> List[ProposalHistoryItem]:
        """Retrieves historical audit entries for a proposal."""
        proposal = self.get_proposal(db, proposal_id, current_user)
        logs = (
            db.query(AuditLog)
            .options(joinedload(AuditLog.actor))
            .filter(AuditLog.entity_type == "proposal", AuditLog.entity_id == proposal_id)
            .order_by(desc(AuditLog.created_at))
            .all()
        )
        history: List[ProposalHistoryItem] = []
        for log in logs:
            actor = log.actor.full_name if log.actor else "System"
            history.append(
                ProposalHistoryItem(
                    action=log.action.value if hasattr(log.action, "value") else str(log.action),
                    timestamp=log.created_at,
                    actor_name=actor,
                    notes=log.description,
                )
            )
        return history


proposal_service = ProposalService()
