"""
Challenge Assignment and Institutional Mandate Service for JanSetu Platform.
Enforces the institutional assignment lifecycle:
INVITED -> ACCEPTED / DECLINED / CANCELLED.
Triggers notifications, audit logging, and automated project workspace provisioning upon acceptance.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.challenge import Challenge
from app.models.challenge_assignment import ChallengeAssignment
from app.models.department import Department
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.schemas.assignment import (
    AssignmentAcceptRequest,
    AssignmentCancelRequest,
    AssignmentCreate,
    AssignmentDeclineRequest,
    AssignmentResponse,
)
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.services.project_service import project_service
from app.utils.enums import (
    AssignmentStatus,
    AuditAction,
    ChallengeStatus,
    NotificationType,
    OrganizationMembershipRole,
    OrganizationType,
    UserRole,
    ValidationStatus,
)


class AssignmentService:
    """Service managing challenge invitations, mandates, acceptance, and cancellation."""

    @staticmethod
    def _is_government_or_platform(user: User) -> bool:
        return user.role in (
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_ADMIN,
            UserRole.DISTRICT_NODAL_OFFICER,
        )

    def _verify_university_admin(self, db: Session, user: User, university_id: str) -> None:
        """Verifies that user is platform admin or an admin/owner of the target university."""
        if user.role == UserRole.PLATFORM_ADMIN:
            return

        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.organization_id == university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if not membership or membership.membership_role not in (
            OrganizationMembershipRole.ADMIN,
            OrganizationMembershipRole.OWNER,
        ):
            raise ForbiddenException("You do not have permission to accept or decline assignments for this university.")

    def create_assignment(
        self,
        db: Session,
        challenge_id: str,
        req: AssignmentCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ChallengeAssignment:
        """Issues an assignment/invitation from government/platform to an accredited university."""
        if not self._is_government_or_platform(current_user):
            raise ForbiddenException("Only authorized government reviewers and platform admins can issue challenge assignments.")

        # 1. Verify Challenge exists and is VALIDATED
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        if challenge.validation_status != ValidationStatus.VALIDATED:
            raise BadRequestException(
                f"Only validated challenges can be assigned. Current validation status: '{challenge.validation_status.value}'."
            )

        # 2. Verify University exists, is active, and is verified
        target_uni_id = req.university_id
        university = db.query(Organization).filter(
            Organization.id == target_uni_id,
            Organization.organization_type == OrganizationType.UNIVERSITY,
        ).first()
        if not university:
            raise NotFoundException(f"University '{target_uni_id}' not found.")

        if not university.is_active:
            raise BadRequestException(f"University '{university.name}' is inactive and cannot receive assignments.")
        if not university.is_verified:
            raise BadRequestException(f"University '{university.name}' is not verified and cannot receive institutional mandates.")

        # 3. Verify Department if provided
        dept = None
        if req.department_id:
            dept = db.query(Department).filter(
                Department.id == req.department_id,
                Department.organization_id == target_uni_id,
            ).first()
            if not dept:
                raise BadRequestException(f"Department '{req.department_id}' does not belong to university '{university.name}'.")

        # 4. Check for duplicate active assignment
        existing = (
            db.query(ChallengeAssignment)
            .filter(
                ChallengeAssignment.challenge_id == challenge_id,
                ChallengeAssignment.university_id == target_uni_id,
                ChallengeAssignment.status.in_([AssignmentStatus.INVITED, AssignmentStatus.ACCEPTED]),
            )
            .first()
        )
        if existing:
            raise ConflictException(
                f"An active assignment already exists for university '{university.name}' on this challenge (Status: {existing.status.value})."
            )

        # 5. Create Assignment
        assignment = ChallengeAssignment(
            challenge_id=challenge_id,
            university_id=target_uni_id,
            department_id=req.department_id,
            assigned_by_user_id=current_user.id,
            status=AssignmentStatus.INVITED,
            invitation_message=req.invitation_message or f"Institutional mandate issued for challenge '{challenge.title}'",
            assigned_at=datetime.now(timezone.utc),
        )
        db.add(assignment)

        # Update Challenge status to ASSIGNED
        challenge.status = ChallengeStatus.ASSIGNED

        db.commit()
        db.refresh(assignment)

        # 6. Audit Log
        audit_service.log_event(
            db=db,
            action=AuditAction.ASSIGN_DEPARTMENT,
            entity_type="challenge_assignment",
            entity_id=assignment.id,
            description=f"Assigned challenge '{challenge.reference_code}' to university '{university.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # 7. Notify University Admins
        uni_admins = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == target_uni_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .all()
        )
        for admin_m in uni_admins:
            notification_service.create_notification(
                db=db,
                recipient_user_id=admin_m.user_id,
                notification_type=NotificationType.DEPARTMENT_ASSIGNED,
                title="New Institutional Mandate Invitation",
                message=f"Government has invited your institution '{university.name}' to solve challenge: '{challenge.title}'.",
                related_challenge_id=challenge.id,
            )

        return assignment

    def accept_assignment(
        self,
        db: Session,
        assignment_id: str,
        req: AssignmentAcceptRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ChallengeAssignment:
        """Accepts an assignment, sets status to ACCEPTED, and triggers project workspace creation."""
        assignment = (
            db.query(ChallengeAssignment)
            .options(
                joinedload(ChallengeAssignment.challenge),
                joinedload(ChallengeAssignment.university),
                joinedload(ChallengeAssignment.department),
            )
            .filter(ChallengeAssignment.id == assignment_id)
            .first()
        )
        if not assignment:
            raise NotFoundException(f"Assignment '{assignment_id}' not found.")

        # RBAC: Only target university admin or platform admin
        self._verify_university_admin(db, current_user, assignment.university_id)

        # Check valid state transition
        if assignment.status == AssignmentStatus.ACCEPTED:
            # Idempotent: provision project workspace if missing, then return
            project_service.get_or_create_project_for_assignment(
                db=db,
                assignment=assignment,
                current_user=current_user,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.commit()
            return assignment

        if assignment.status != AssignmentStatus.INVITED:
            raise BadRequestException(f"Cannot accept assignment in '{assignment.status.value}' status.")

        assignment.status = AssignmentStatus.ACCEPTED
        assignment.responded_at = datetime.now(timezone.utc)
        if req.response_message:
            assignment.response_message = req.response_message

        # Ensure challenge is flagged as assigned
        if assignment.challenge:
            assignment.challenge.status = ChallengeStatus.ASSIGNED

        # Automatically provision Project Workspace
        project = project_service.get_or_create_project_for_assignment(
            db=db,
            assignment=assignment,
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.commit()
        db.refresh(assignment)

        # Audit Log
        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="challenge_assignment",
            entity_id=assignment.id,
            description=f"University '{assignment.university.name}' accepted mandate for challenge '{assignment.challenge.reference_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Notify Assigner (Government)
        notification_service.create_notification(
            db=db,
            recipient_user_id=assignment.assigned_by_user_id,
            notification_type=NotificationType.SYSTEM,
            title="Institutional Mandate Accepted",
            message=f"University '{assignment.university.name}' has accepted the mandate for challenge '{assignment.challenge.title}'. Project workspace initialized ({project.project_code}).",
            related_challenge_id=assignment.challenge_id,
        )

        return assignment

    def decline_assignment(
        self,
        db: Session,
        assignment_id: str,
        req: AssignmentDeclineRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ChallengeAssignment:
        """Declines an assignment invitation."""
        assignment = (
            db.query(ChallengeAssignment)
            .options(
                joinedload(ChallengeAssignment.challenge),
                joinedload(ChallengeAssignment.university),
            )
            .filter(ChallengeAssignment.id == assignment_id)
            .first()
        )
        if not assignment:
            raise NotFoundException(f"Assignment '{assignment_id}' not found.")

        # RBAC: Only target university admin or platform admin
        self._verify_university_admin(db, current_user, assignment.university_id)

        if assignment.status != AssignmentStatus.INVITED:
            raise BadRequestException(f"Cannot decline assignment in '{assignment.status.value}' status.")

        assignment.status = AssignmentStatus.DECLINED
        assignment.responded_at = datetime.now(timezone.utc)
        if req.response_message:
            assignment.response_message = req.response_message

        # If no other active accepted assignments exist for this challenge, return challenge to VALIDATED
        active_remaining = (
            db.query(ChallengeAssignment)
            .filter(
                ChallengeAssignment.challenge_id == assignment.challenge_id,
                ChallengeAssignment.id != assignment.id,
                ChallengeAssignment.status == AssignmentStatus.ACCEPTED,
            )
            .first()
        )
        if not active_remaining and assignment.challenge:
            assignment.challenge.status = ChallengeStatus.VALIDATED

        db.commit()
        db.refresh(assignment)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="challenge_assignment",
            entity_id=assignment.id,
            description=f"University '{assignment.university.name}' declined mandate for challenge '{assignment.challenge.reference_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Notify Assigner
        notification_service.create_notification(
            db=db,
            recipient_user_id=assignment.assigned_by_user_id,
            notification_type=NotificationType.SYSTEM,
            title="Institutional Mandate Declined",
            message=f"University '{assignment.university.name}' declined the mandate for challenge '{assignment.challenge.title}'. Reason: {req.response_message or 'Capacity constraints'}",
            related_challenge_id=assignment.challenge_id,
        )

        return assignment

    def cancel_assignment(
        self,
        db: Session,
        assignment_id: str,
        req: AssignmentCancelRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ChallengeAssignment:
        """Cancels an assignment invitation by government or platform admin."""
        if not self._is_government_or_platform(current_user):
            raise ForbiddenException("Only government or platform administrators can cancel assignments.")

        assignment = (
            db.query(ChallengeAssignment)
            .options(
                joinedload(ChallengeAssignment.challenge),
                joinedload(ChallengeAssignment.university),
            )
            .filter(ChallengeAssignment.id == assignment_id)
            .first()
        )
        if not assignment:
            raise NotFoundException(f"Assignment '{assignment_id}' not found.")

        if assignment.status not in (AssignmentStatus.INVITED, AssignmentStatus.ACCEPTED):
            raise BadRequestException(f"Cannot cancel assignment in '{assignment.status.value}' status.")

        assignment.status = AssignmentStatus.CANCELLED
        assignment.responded_at = datetime.now(timezone.utc)
        if req.reason:
            assignment.response_message = f"Cancelled by government: {req.reason}"

        # If challenge has no other accepted assignments, return to VALIDATED
        active_remaining = (
            db.query(ChallengeAssignment)
            .filter(
                ChallengeAssignment.challenge_id == assignment.challenge_id,
                ChallengeAssignment.id != assignment.id,
                ChallengeAssignment.status == AssignmentStatus.ACCEPTED,
            )
            .first()
        )
        if not active_remaining and assignment.challenge:
            assignment.challenge.status = ChallengeStatus.VALIDATED

        db.commit()
        db.refresh(assignment)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="challenge_assignment",
            entity_id=assignment.id,
            description=f"Cancelled assignment for university '{assignment.university.name}' on challenge '{assignment.challenge.reference_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return assignment

    def list_assignments_for_challenge(self, db: Session, challenge_id: str) -> List[ChallengeAssignment]:
        """Lists assignments for a specific challenge."""
        return (
            db.query(ChallengeAssignment)
            .options(
                joinedload(ChallengeAssignment.university),
                joinedload(ChallengeAssignment.department),
            )
            .filter(ChallengeAssignment.challenge_id == challenge_id)
            .order_by(desc(ChallengeAssignment.created_at))
            .all()
        )

    def list_assignments_for_university(self, db: Session, university_id: str) -> List[ChallengeAssignment]:
        """Lists assignments for a specific university."""
        return (
            db.query(ChallengeAssignment)
            .options(
                joinedload(ChallengeAssignment.challenge),
                joinedload(ChallengeAssignment.department),
            )
            .filter(ChallengeAssignment.university_id == university_id)
            .order_by(desc(ChallengeAssignment.created_at))
            .all()
        )

    def serialize_assignment_response(self, assignment: ChallengeAssignment) -> AssignmentResponse:
        """Formats ChallengeAssignment into standard AssignmentResponse schema."""
        return AssignmentResponse(
            id=assignment.id,
            challenge_id=assignment.challenge_id,
            university_id=assignment.university_id,
            university_name=assignment.university.name if assignment.university else None,
            department_id=assignment.department_id,
            department_name=assignment.department.name if assignment.department else None,
            assigned_by_user_id=assignment.assigned_by_user_id,
            status=assignment.status,
            invitation_message=assignment.invitation_message,
            response_message=assignment.response_message,
            assigned_at=assignment.assigned_at,
            responded_at=assignment.responded_at,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )


assignment_service = AssignmentService()
