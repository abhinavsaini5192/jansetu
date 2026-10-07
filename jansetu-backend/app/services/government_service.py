"""
Government Validation Service for JanSetu Platform.
Enforces the official state transition machine for societal challenges,
restricts actions to authorized government nodal officers and platform admins,
and triggers notifications and immutable audit logs.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.core.logging_config import logger
from app.models.challenge import Challenge
from app.models.government_review import GovernmentReview
from app.models.user import User
from app.schemas.government import GovernmentDecisionRequest
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.utils.enums import (
    AuditAction,
    ChallengeStatus,
    NotificationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)

# Authorized government review roles
GOVERNMENT_REVIEWER_ROLES = {
    UserRole.GOVERNMENT_ADMIN,
    UserRole.DISTRICT_NODAL_OFFICER,
    UserRole.PLATFORM_ADMIN,
}

# Standard official government departments in Jharkhand
OFFICIAL_DEPARTMENTS: List[str] = [
    "Department of Drinking Water & Sanitation",
    "Department of Rural Development",
    "Department of Agriculture, Animal Husbandry & Co-operative",
    "Department of Health, Medical Education & Family Welfare",
    "Department of School Education & Literacy",
    "Department of Road Construction",
    "Department of Energy",
    "Department of Women, Child Development & Social Security",
    "Department of Scheduled Tribe, Scheduled Caste & Backward Class Welfare",
    "Department of Urban Development & Housing",
    "Department of Forest, Environment & Climate Change",
    "Department of Labour, Employment, Training & Skill Development",
]


class GovernmentService:
    """Service handling government verification workflows and challenge progression."""

    def verify_government_role(self, current_user: User) -> None:
        """Ensures caller has official government verification authority."""
        if current_user.role not in GOVERNMENT_REVIEWER_ROLES:
            raise ForbiddenException(
                "Access restricted: Only government administrators, district nodal officers, "
                "or platform administrators can review challenges."
            )

    def list_pending_queue(
        self,
        db: Session,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        district: Optional[str] = None,
        domain: Optional[SocietalDomain] = None,
        status: Optional[ChallengeStatus] = None,
        validation_status: Optional[ValidationStatus] = None,
        priority: Optional[PriorityLevel] = None,
        urgency: Optional[UrgencyLevel] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Challenge], int, int]:
        """
        Lists challenges awaiting review or action in the government queue.
        By default returns SUBMITTED, UNDER_REVIEW, and NEEDS_CLARIFICATION items.
        """
        self.verify_government_role(current_user)

        query = select(Challenge).options(
            joinedload(Challenge.submitted_by_user),
            joinedload(Challenge.submitted_by_organization),
        )

        # Status filter
        if status:
            query = query.where(Challenge.status == status)
        elif not validation_status:
            # Default queue: submitted, under_review, needs_clarification
            query = query.where(
                Challenge.status.in_([
                    ChallengeStatus.SUBMITTED,
                    ChallengeStatus.UNDER_REVIEW,
                    ChallengeStatus.NEEDS_CLARIFICATION,
                ])
            )

        if validation_status:
            query = query.where(Challenge.validation_status == validation_status)

        if district and district.strip():
            query = query.where(func.lower(Challenge.district) == district.strip().lower())

        if domain is not None:
            query = query.where(Challenge.domain == domain)

        if priority is not None:
            query = query.where(Challenge.priority == priority)

        if urgency is not None:
            query = query.where(Challenge.urgency == urgency)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Challenge.title).like(term),
                    func.lower(Challenge.description).like(term),
                    func.lower(Challenge.reference_code).like(term),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        # Sort priority/urgency and created_at desc
        skip = (page - 1) * page_size
        stmt = query.order_by(desc(Challenge.created_at)).offset(skip).limit(page_size)
        items = list(db.scalars(stmt).unique().all())

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return items, total, total_pages

    def get_challenge_detail(self, db: Session, challenge_id: str, current_user: User) -> Challenge:
        """Retrieves complete challenge record for a government reviewer."""
        self.verify_government_role(current_user)
        challenge = (
            db.query(Challenge)
            .options(
                joinedload(Challenge.submitted_by_user),
                joinedload(Challenge.submitted_by_organization),
                joinedload(Challenge.attachments),
                joinedload(Challenge.reviews),
            )
            .filter(Challenge.id == challenge_id)
            .first()
        )
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")
        return challenge

    def review_challenge(
        self,
        db: Session,
        challenge_id: str,
        decision_req: GovernmentDecisionRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[Challenge, GovernmentReview]:
        """
        Executes a human-authorized government review decision on a challenge.
        Validates state machine transitions, updates records, and creates notifications and audit logs.
        """
        self.verify_government_role(current_user)

        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        current_status = challenge.status
        decision = decision_req.decision.strip().lower()
        now = datetime.now(timezone.utc)

        # Enforce terminal state restrictions
        if current_status in (ChallengeStatus.REJECTED, ChallengeStatus.DUPLICATE):
            raise BadRequestException(
                f"Challenge is in terminal status '{current_status.value}' and cannot be reviewed further."
            )

        new_status: ChallengeStatus
        new_validation_status: ValidationStatus
        audit_action: AuditAction
        notif_type: NotificationType
        notif_title: str
        notif_message: str

        if decision == "move_to_review":
            if current_status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.NEEDS_CLARIFICATION):
                raise BadRequestException(
                    f"Cannot move to review from current status '{current_status.value}'."
                )
            new_status = ChallengeStatus.UNDER_REVIEW
            new_validation_status = ValidationStatus.PENDING
            audit_action = AuditAction.STATUS_CHANGE
            notif_type = NotificationType.SYSTEM
            notif_title = "Challenge Under Review"
            notif_message = f"Your challenge '{challenge.title}' is now actively under government review."

        elif decision == "validate":
            if current_status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.UNDER_REVIEW, ChallengeStatus.NEEDS_CLARIFICATION):
                raise BadRequestException(
                    f"Cannot validate challenge from status '{current_status.value}'."
                )
            new_status = ChallengeStatus.VALIDATED
            new_validation_status = ValidationStatus.VALIDATED
            challenge.validated_at = now
            audit_action = AuditAction.VALIDATE
            notif_type = NotificationType.CHALLENGE_VALIDATED
            notif_title = "Challenge Validated"
            dept_text = f" and assigned to {decision_req.department}" if decision_req.department else ""
            notif_message = (
                f"Congratulations! Your challenge '{challenge.title}' has been officially validated{dept_text}."
            )

        elif decision == "reject":
            if current_status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.UNDER_REVIEW, ChallengeStatus.NEEDS_CLARIFICATION):
                raise BadRequestException(
                    f"Cannot reject challenge from status '{current_status.value}'."
                )
            if not decision_req.rejection_reason and not decision_req.review_comment:
                raise BadRequestException("A rejection reason or review comment is required when rejecting a challenge.")

            new_status = ChallengeStatus.REJECTED
            new_validation_status = ValidationStatus.REJECTED
            challenge.rejected_at = now
            audit_action = AuditAction.REJECT
            notif_type = NotificationType.CHALLENGE_REJECTED
            notif_title = "Challenge Rejected"
            reason_text = decision_req.rejection_reason or decision_req.review_comment
            notif_message = f"Your challenge '{challenge.title}' could not be validated. Reason: {reason_text}"

        elif decision == "mark_duplicate":
            if current_status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.UNDER_REVIEW, ChallengeStatus.NEEDS_CLARIFICATION):
                raise BadRequestException(
                    f"Cannot mark duplicate from status '{current_status.value}'."
                )
            if not decision_req.duplicate_of_challenge_id:
                raise BadRequestException("Duplicate target challenge ID is required when marking as duplicate.")

            dup_target = db.query(Challenge).filter(Challenge.id == decision_req.duplicate_of_challenge_id).first()
            if not dup_target:
                raise NotFoundException("Target duplicate challenge does not exist.")
            if dup_target.id == challenge.id:
                raise BadRequestException("A challenge cannot be a duplicate of itself.")

            new_status = ChallengeStatus.DUPLICATE
            new_validation_status = ValidationStatus.DUPLICATE
            challenge.duplicate_of_challenge_id = dup_target.id
            audit_action = AuditAction.MARK_DUPLICATE
            notif_type = NotificationType.CHALLENGE_MARKED_DUPLICATE
            notif_title = "Challenge Linked as Duplicate"
            notif_message = (
                f"Your challenge '{challenge.title}' has been identified as a duplicate of {dup_target.reference_code}."
            )

        elif decision == "request_clarification":
            if current_status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.UNDER_REVIEW):
                raise BadRequestException(
                    f"Cannot request clarification from status '{current_status.value}'."
                )
            clarification = decision_req.clarification_request or decision_req.review_comment
            if not clarification:
                raise BadRequestException("A clarification request message is required.")

            new_status = ChallengeStatus.NEEDS_CLARIFICATION
            new_validation_status = ValidationStatus.NEEDS_CLARIFICATION
            audit_action = AuditAction.REQUEST_CLARIFICATION
            notif_type = NotificationType.CLARIFICATION_REQUESTED
            notif_title = "Clarification Requested"
            notif_message = (
                f"A government reviewer requested clarification on '{challenge.title}': {clarification}"
            )

        elif decision == "assign_department":
            if not decision_req.department:
                raise BadRequestException("Department name is required for department assignment.")
            challenge.assigned_department = decision_req.department
            if challenge.status == ChallengeStatus.VALIDATED:
                new_status = ChallengeStatus.ASSIGNED
                new_validation_status = ValidationStatus.VALIDATED
            else:
                new_status = challenge.status
                new_validation_status = challenge.validation_status

            audit_action = AuditAction.ASSIGN_DEPARTMENT
            notif_type = NotificationType.DEPARTMENT_ASSIGNED
            notif_title = "Department Assigned"
            notif_message = (
                f"Your challenge '{challenge.title}' has been assigned to: {decision_req.department}"
            )

        else:
            raise BadRequestException(
                f"Invalid decision '{decision}'. Must be one of: move_to_review, validate, "
                "reject, mark_duplicate, request_clarification, assign_department."
            )

        # Department assignment can accompany other decisions (e.g. validate with department)
        if decision_req.department:
            challenge.assigned_department = decision_req.department

        # Record review comment
        comment_text = decision_req.review_comment or f"Decision '{decision}' recorded by reviewer."

        # Create review entity
        review = GovernmentReview(
            challenge_id=challenge.id,
            reviewer_user_id=current_user.id,
            previous_status=current_status.value,
            new_status=new_status.value,
            validation_status=new_validation_status.value,
            review_comment=comment_text,
            rejection_reason=decision_req.rejection_reason,
            duplicate_of_challenge_id=decision_req.duplicate_of_challenge_id,
            clarification_request=decision_req.clarification_request,
            reviewed_at=now,
        )

        # Update challenge status
        challenge.status = new_status
        challenge.validation_status = new_validation_status

        db.add(review)
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        db.refresh(review)

        # Generate in-app notification to challenge submitter
        notification_service.create_notification(
            db=db,
            recipient_user_id=challenge.submitted_by_user_id,
            notification_type=notif_type,
            title=notif_title,
            message=notif_message,
            related_challenge_id=challenge.id,
        )

        # Record immutable audit log
        audit_service.record_audit_event(
            db=db,
            action=audit_action,
            entity_type="challenge",
            entity_id=challenge.id,
            description=f"Government review decision '{decision}' applied to challenge {challenge.reference_code}.",
            actor=current_user,
            metadata={
                "previous_status": current_status.value,
                "new_status": new_status.value,
                "reviewer_id": current_user.id,
                "reviewer_role": current_user.role.value,
                "department": challenge.assigned_department,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(
            f"Review applied to challenge [{challenge.reference_code}] by [{current_user.id}]: "
            f"{current_status.value} -> {new_status.value}"
        )
        return challenge, review

    def get_review_history(self, db: Session, challenge_id: str, current_user: User) -> List[GovernmentReview]:
        """Retrieves chronological review history for a challenge."""
        self.verify_government_role(current_user)
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        return (
            db.query(GovernmentReview)
            .options(joinedload(GovernmentReview.reviewer_user))
            .filter(GovernmentReview.challenge_id == challenge_id)
            .order_by(GovernmentReview.reviewed_at.desc())
            .all()
        )

    def get_official_departments(self) -> List[str]:
        """Returns list of recognized Jharkhand state government departments."""
        return OFFICIAL_DEPARTMENTS


government_service = GovernmentService()
