"""
Government Validation & Workflow API Routes.
Provides endpoints for government administrators and district nodal officers
to review, validate, reject, link duplicates, request clarification, and assign departments.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.challenge import ChallengeDetailResponse, ChallengeResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMetadata
from app.schemas.government import (
    GovernmentDecisionRequest,
    GovernmentReviewHistoryResponse,
    GovernmentReviewResponse,
)
from app.services.government_service import government_service
from app.utils.constants import get_canonical_district, is_valid_district
from app.utils.enums import (
    ChallengeStatus,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    ValidationStatus,
    normalize_enum_value,
)

router = APIRouter()


@router.get(
    "/challenges/pending",
    response_model=PaginatedResponse[ChallengeResponse],
    status_code=status.HTTP_200_OK,
    summary="Government Pending Verification Queue",
    description="Retrieves the official verification queue of challenges requiring review. Restricted to government roles.",
)
@router.get(
    "/validation-queue",
    response_model=PaginatedResponse[ChallengeResponse],
    status_code=status.HTTP_200_OK,
    summary="Frontend Validation Queue Alias",
    include_in_schema=False,
)
def get_pending_queue(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Frontend alias for page_size"),
    district: Optional[str] = Query(None, description="Filter by district"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by challenge status"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    urgency: Optional[str] = Query(None, description="Filter by urgency level"),
    search: Optional[str] = Query(None, description="Keyword search in title, description, or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> PaginatedResponse[ChallengeResponse]:
    """List challenges requiring government review."""
    effective_limit = limit or page_size or 20

    norm_domain = normalize_enum_value(SocietalDomain, domain) if domain else None
    norm_status = normalize_enum_value(ChallengeStatus, status_filter) if status_filter else None
    norm_val_status = normalize_enum_value(ValidationStatus, validation_status) if validation_status else None
    norm_priority = normalize_enum_value(PriorityLevel, priority) if priority else None
    norm_urgency = normalize_enum_value(UrgencyLevel, urgency) if urgency else None
    canonical_district = get_canonical_district(district) if district and is_valid_district(district) else district

    items, total, total_pages = government_service.list_pending_queue(
        db=db,
        current_user=current_user,
        page=page,
        page_size=effective_limit,
        district=canonical_district,
        domain=norm_domain,
        status=norm_status,
        validation_status=norm_val_status,
        priority=norm_priority,
        urgency=norm_urgency,
        search=search,
    )

    serialized = [ChallengeResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        success=True,
        data=serialized,
        items=serialized,
        pagination=PaginationMetadata(
            page=page,
            page_size=effective_limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/challenges/{challenge_id}",
    response_model=ChallengeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Government Challenge Detail",
    description="Fetches full details including submitter, location, attachments, and past review actions.",
)
def get_government_challenge_detail(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ChallengeDetailResponse:
    """Retrieve full challenge record for government review."""
    challenge = government_service.get_challenge_detail(db, challenge_id, current_user)
    return ChallengeDetailResponse.model_validate(challenge)


@router.post(
    "/challenges/{challenge_id}/review",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Submit Government Review Decision",
    description="Submits an official verification decision (move_to_review, validate, reject, mark_duplicate, request_clarification).",
)
def review_challenge(
    challenge_id: str,
    decision_req: GovernmentDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Execute official government review action on a challenge."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    challenge, review = government_service.review_challenge(
        db=db,
        challenge_id=challenge_id,
        decision_req=decision_req,
        current_user=current_user,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    return ApiResponse(
        success=True,
        message=f"Challenge status successfully transitioned to '{challenge.status.value}'.",
        data={
            "challenge_id": challenge.id,
            "status": challenge.status.value,
            "validation_status": challenge.validation_status.value,
            "review_id": review.id,
            "assigned_department": challenge.assigned_department,
        },
    )


@router.get(
    "/challenges/{challenge_id}/review-history",
    response_model=GovernmentReviewHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Government Review History",
    description="Lists all historical review decisions and remarks for a challenge in reverse chronological order.",
)
def get_review_history(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> GovernmentReviewHistoryResponse:
    """Fetch chronological review history."""
    reviews = government_service.get_review_history(db, challenge_id, current_user)
    serialized = [GovernmentReviewResponse.model_validate(r) for r in reviews]
    return GovernmentReviewHistoryResponse(
        challenge_id=challenge_id,
        history=serialized,
        total=len(serialized),
    )


# ---------------------------------------------------------------------------
# Frontend Compatibility Convenience Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/challenges/{challenge_id}/validate",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Frontend Validate Challenge Shortcut",
)
def validate_challenge_convenience(
    challenge_id: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Shortcut endpoint for validating a challenge."""
    remarks = payload.get("remarks") or payload.get("review_comment") or "Validated by reviewer"
    dept = payload.get("department")
    decision_req = GovernmentDecisionRequest(
        decision="validate",
        review_comment=remarks,
        department=dept,
    )
    challenge, review = government_service.review_challenge(
        db=db,
        challenge_id=challenge_id,
        decision_req=decision_req,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return ApiResponse(
        success=True,
        message="Challenge successfully validated.",
        data={
            "challenge_id": challenge.id,
            "status": challenge.status.value,
            "validation_status": challenge.validation_status.value,
            "review_id": review.id,
        },
    )


@router.post(
    "/challenges/{challenge_id}/reject",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Frontend Reject Challenge Shortcut",
)
def reject_challenge_convenience(
    challenge_id: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Shortcut endpoint for rejecting a challenge."""
    reason = payload.get("reason") or payload.get("rejection_reason") or "Rejected by reviewer"
    decision_req = GovernmentDecisionRequest(
        decision="reject",
        rejection_reason=reason,
        review_comment=reason,
    )
    challenge, review = government_service.review_challenge(
        db=db,
        challenge_id=challenge_id,
        decision_req=decision_req,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return ApiResponse(
        success=True,
        message="Challenge successfully rejected.",
        data={
            "challenge_id": challenge.id,
            "status": challenge.status.value,
            "validation_status": challenge.validation_status.value,
            "review_id": review.id,
        },
    )


@router.post(
    "/challenges/{challenge_id}/assign-department",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Frontend Assign Department Shortcut",
)
def assign_department_convenience(
    challenge_id: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Shortcut endpoint for assigning a department to a challenge."""
    dept = payload.get("department")
    decision_req = GovernmentDecisionRequest(
        decision="assign_department",
        department=dept,
        review_comment=f"Assigned to {dept}",
    )
    challenge, review = government_service.review_challenge(
        db=db,
        challenge_id=challenge_id,
        decision_req=decision_req,
        current_user=current_user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return ApiResponse(
        success=True,
        message="Department successfully assigned.",
        data={
            "challenge_id": challenge.id,
            "assigned_department": challenge.assigned_department,
            "status": challenge.status.value,
            "validation_status": challenge.validation_status.value,
        },
    )


@router.get(
    "/departments",
    response_model=ApiResponse[List[str]],
    status_code=status.HTTP_200_OK,
    summary="List Official Government Departments",
    description="Returns list of official Jharkhand state government departments for nodal assignment.",
)
def list_official_departments() -> ApiResponse[List[str]]:
    """List recognized government departments."""
    depts = government_service.get_official_departments()
    return ApiResponse(
        success=True,
        message="Departments retrieved successfully.",
        data=depts,
    )
