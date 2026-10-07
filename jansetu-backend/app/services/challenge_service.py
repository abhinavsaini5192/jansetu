"""
Business Logic Service for Societal Challenges Management.
Enforces submitter attribution, lifecycle immutability, ownership authorization,
and query filtering.
"""
from datetime import datetime, timezone
from math import ceil
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.challenge import Challenge
from app.models.user import User
from app.repositories.challenge_repository import (
    ChallengeRepository,
    challenge_repository,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
    organization_repository,
)
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeUpdateRequest,
)
from app.utils.constants import get_canonical_district, is_valid_district
from app.utils.enums import (
    ChallengeStatus,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
    normalize_enum_value,
)


class ChallengeService:
    """Service handling business domain logic for societal challenges."""

    def __init__(
        self,
        challenge_repo: ChallengeRepository = challenge_repository,
        org_repo: OrganizationRepository = organization_repository,
    ):
        self.challenge_repo = challenge_repo
        self.org_repo = org_repo

    def create_challenge(
        self,
        db: Session,
        payload: ChallengeCreateRequest,
        current_user: User,
    ) -> Challenge:
        """
        Creates a new challenge record.
        - Automatically assigns current_user as submitter (never trusts client ID).
        - Validates submitting organization membership if specified.
        - Sets initial status to SUBMITTED and validation_status to PENDING.
        """
        # Validate submitting organization affiliation if specified
        org_id = payload.submitted_by_organization_id
        if org_id:
            org = self.org_repo.get_by_id(db, org_id)
            if not org:
                raise NotFoundException(message=f"Submitting organization '{org_id}' not found.")
            
            # Check user membership in the organization
            if current_user.role != UserRole.PLATFORM_ADMIN:
                membership = self.org_repo.get_membership(db, current_user.id, org_id)
                if not membership or not membership.is_active:
                    raise ForbiddenException(
                        message="You are not an active member of the specified submitting organization."
                    )

        challenge = Challenge(
            submitted_by_user_id=current_user.id,
            submitted_by_organization_id=org_id,
            title=payload.title,
            title_hi=payload.title_hi,
            description=payload.description,
            problem_statement=payload.problem_statement,
            proposed_context=payload.proposed_context,
            district=payload.district,
            block=payload.block,
            village_or_ward=payload.village_or_ward,
            location_description=payload.location_description,
            domain=payload.domain,
            subdomain=payload.subdomain,
            priority=payload.priority or PriorityLevel.MEDIUM,
            urgency=payload.urgency or UrgencyLevel.MEDIUM,
            status=ChallengeStatus.SUBMITTED,
            validation_status=ValidationStatus.PENDING,
            affected_population=payload.affected_population,
            estimated_beneficiaries=payload.estimated_beneficiaries,
            existing_attempts=payload.existing_attempts,
            expected_outcome=payload.expected_outcome,
            constraints=payload.constraints,
            submitted_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return self.challenge_repo.create_challenge(db, challenge)

    def get_challenge(
        self,
        db: Session,
        challenge_id: str,
    ) -> Challenge:
        """Fetch a challenge by its primary key ID or raise 404."""
        challenge = self.challenge_repo.get_challenge_by_id(db, challenge_id)
        if not challenge:
            raise NotFoundException(message=f"Challenge with ID '{challenge_id}' not found.")
        return challenge

    def list_challenges(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        district: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        urgency: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Challenge], int, int]:
        """
        Public/authenticated list of challenges with filters and pagination.
        Returns a tuple of (items, total_count, total_pages).
        """
        effective_page = max(1, page)
        effective_limit = min(100, max(1, page_size))
        skip = (effective_page - 1) * effective_limit

        # Validate and canonicalize district if supplied
        canonical_district = None
        if district and district.strip():
            if not is_valid_district(district):
                raise BadRequestException(
                    message=f"District '{district}' is not a recognized Jharkhand district."
                )
            canonical_district = get_canonical_district(district)

        # Validate enum filters if supplied
        resolved_domain = None
        if domain and str(domain).strip():
            resolved_domain = normalize_enum_value(SocietalDomain, str(domain).strip())
            if resolved_domain is None:
                raise BadRequestException(message=f"Invalid domain filter '{domain}'.")

        resolved_status = None
        if status and str(status).strip():
            resolved_status = normalize_enum_value(ChallengeStatus, str(status).strip())
            if resolved_status is None:
                raise BadRequestException(message=f"Invalid status filter '{status}'.")

        resolved_priority = None
        if priority and str(priority).strip():
            resolved_priority = normalize_enum_value(PriorityLevel, str(priority).strip())
            if resolved_priority is None:
                raise BadRequestException(message=f"Invalid priority filter '{priority}'.")

        resolved_urgency = None
        if urgency and str(urgency).strip():
            resolved_urgency = normalize_enum_value(UrgencyLevel, str(urgency).strip())
            if resolved_urgency is None:
                raise BadRequestException(message=f"Invalid urgency filter '{urgency}'.")

        items, total = self.challenge_repo.list_challenges(
            db=db,
            skip=skip,
            limit=effective_limit,
            district=canonical_district,
            domain=resolved_domain,
            status=resolved_status,
            priority=resolved_priority,
            urgency=resolved_urgency,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = ceil(total / effective_limit) if total > 0 else 0
        return items, total, total_pages

    def list_user_challenges(
        self,
        db: Session,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        district: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Challenge], int, int]:
        """
        List only the authenticated user's submitted challenges.
        Never allows querying another user's submissions.
        """
        effective_page = max(1, page)
        effective_limit = min(100, max(1, page_size))
        skip = (effective_page - 1) * effective_limit

        canonical_district = None
        if district and district.strip():
            canonical_district = get_canonical_district(district)

        resolved_domain = None
        if domain and str(domain).strip():
            resolved_domain = normalize_enum_value(SocietalDomain, str(domain).strip())

        resolved_status = None
        if status and str(status).strip():
            resolved_status = normalize_enum_value(ChallengeStatus, str(status).strip())

        items, total = self.challenge_repo.list_user_challenges(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=effective_limit,
            district=canonical_district,
            domain=resolved_domain,
            status=resolved_status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = ceil(total / effective_limit) if total > 0 else 0
        return items, total, total_pages

    def update_challenge(
        self,
        db: Session,
        challenge_id: str,
        payload: ChallengeUpdateRequest,
        current_user: User,
    ) -> Challenge:
        """
        Updates an existing challenge.
        - Enforces submitter ownership (or platform admin).
        - Prevents edits once officially reviewed/validated or rejected.
        - Prevents client modifications to workflow or submitter identity fields.
        """
        challenge = self.get_challenge(db, challenge_id)

        # Enforce submitter ownership
        if challenge.submitted_by_user_id != current_user.id and current_user.role != UserRole.PLATFORM_ADMIN:
            raise ForbiddenException(message="You do not have permission to update this challenge.")

        # Workflow lock check: Normal submitters cannot edit after review begins or decision is reached
        locked_statuses = {
            ChallengeStatus.VALIDATED,
            ChallengeStatus.REJECTED,
            ChallengeStatus.ASSIGNED,
        }
        if challenge.status in locked_statuses or challenge.validation_status != ValidationStatus.PENDING:
            raise ForbiddenException(
                message=f"Challenge is locked in '{challenge.status.value}' status and cannot be modified."
            )

        # Apply allowed update fields
        if payload.title is not None:
            challenge.title = payload.title
        if payload.title_hi is not None:
            challenge.title_hi = payload.title_hi
        if payload.description is not None:
            challenge.description = payload.description
        if payload.problem_statement is not None:
            challenge.problem_statement = payload.problem_statement
        if payload.proposed_context is not None:
            challenge.proposed_context = payload.proposed_context
        if payload.district is not None:
            challenge.district = payload.district
        if payload.block is not None:
            challenge.block = payload.block
        if payload.village_or_ward is not None:
            challenge.village_or_ward = payload.village_or_ward
        if payload.location_description is not None:
            challenge.location_description = payload.location_description
        if payload.domain is not None:
            challenge.domain = payload.domain
        if payload.subdomain is not None:
            challenge.subdomain = payload.subdomain
        if payload.priority is not None:
            challenge.priority = payload.priority
        if payload.urgency is not None:
            challenge.urgency = payload.urgency
        if payload.affected_population is not None:
            challenge.affected_population = payload.affected_population
        if payload.estimated_beneficiaries is not None:
            challenge.estimated_beneficiaries = payload.estimated_beneficiaries
        if payload.existing_attempts is not None:
            challenge.existing_attempts = payload.existing_attempts
        if payload.expected_outcome is not None:
            challenge.expected_outcome = payload.expected_outcome
        if payload.constraints is not None:
            challenge.constraints = payload.constraints

        challenge.updated_at = datetime.now(timezone.utc)
        return self.challenge_repo.update_challenge(db, challenge)

    def delete_challenge(
        self,
        db: Session,
        challenge_id: str,
        current_user: User,
    ) -> None:
        """
        Deletes a challenge before review begins.
        - Only the original submitter or platform admin may delete.
        - Deletion is prohibited once review begins or when challenge is validated/assigned.
        """
        challenge = self.get_challenge(db, challenge_id)

        # Enforce submitter ownership
        if challenge.submitted_by_user_id != current_user.id and current_user.role != UserRole.PLATFORM_ADMIN:
            raise ForbiddenException(message="You do not have permission to delete this challenge.")

        # Review lock check
        locked_statuses = {
            ChallengeStatus.UNDER_REVIEW,
            ChallengeStatus.VALIDATED,
            ChallengeStatus.REJECTED,
            ChallengeStatus.DUPLICATE,
            ChallengeStatus.ASSIGNED,
        }
        if challenge.status in locked_statuses or challenge.validation_status != ValidationStatus.PENDING:
            raise ForbiddenException(
                message=f"Challenge cannot be deleted while in '{challenge.status.value}' review state."
            )

        self.challenge_repo.delete_challenge(db, challenge)


challenge_service = ChallengeService()
