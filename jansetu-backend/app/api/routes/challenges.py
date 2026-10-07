"""
Challenge Management API Routes.
Provides endpoints for creating, reading, updating, listing, and deleting societal challenges.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional, require_authenticated_user
from app.core.security import hash_password
from app.models.user import User
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeDetailResponse,
    ChallengeResponse,
    ChallengeUpdateRequest,
)
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMetadata
from app.services.challenge_service import challenge_service
from app.utils.enums import UserRole

router = APIRouter()


@router.post(
    "",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Challenge",
    description="Submits a new societal challenge. Supports logged-in users and anonymous citizen crowdsourcing submissions.",
)
def create_challenge(
    payload: ChallengeCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ChallengeResponse:
    """Create a new societal challenge."""
    if not current_user:
        # Resolve or auto-provision standard citizen user for public intake
        default_citizen = db.query(User).filter(User.email == "citizen@jansetu.gov.in").first()
        if not default_citizen:
            default_citizen = User(
                email="citizen@jansetu.gov.in",
                full_name="Citizen Submitter",
                password_hash=hash_password("JanSetuCitizen2026!"),
                role=UserRole.CITIZEN,
                is_active=True,
                is_verified=True,
            )
            db.add(default_citizen)
            db.flush()
        current_user = default_citizen

    challenge = challenge_service.create_challenge(db, payload, current_user)
    return ChallengeResponse.model_validate(challenge)


@router.get(
    "",
    response_model=PaginatedResponse[ChallengeResponse],
    status_code=status.HTTP_200_OK,
    summary="List Challenges",
    description="Public paginated listing of societal challenges with optional filters and full-text keyword search.",
)
def list_challenges(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Frontend alias for page_size"),
    district: Optional[str] = Query(None, description="Filter by Jharkhand district"),
    domain: Optional[str] = Query(None, description="Filter by societal domain"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by challenge status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    urgency: Optional[str] = Query(None, description="Filter by urgency level"),
    search: Optional[str] = Query(None, description="Full-text search in title, description, and reference code"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sortBy: Optional[str] = Query(None, description="Frontend alias for sort_by"),
    sort_order: Optional[str] = Query(None, description="Sort direction ('asc' or 'desc')"),
    order: Optional[str] = Query(None, description="Frontend alias for sort_order"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ChallengeResponse]:
    """List challenges with filtering and pagination."""
    effective_limit = limit or page_size or 20
    effective_sort_by = sortBy or sort_by or "created_at"
    effective_sort_order = order or sort_order or "desc"

    # Normalize camelCase frontend sort fields
    if effective_sort_by == "submittedAt":
        effective_sort_by = "submitted_at"
    elif effective_sort_by == "createdAt":
        effective_sort_by = "created_at"

    items, total, total_pages = challenge_service.list_challenges(
        db=db,
        page=page,
        page_size=effective_limit,
        district=district,
        domain=domain,
        status=status_filter,
        priority=priority,
        urgency=urgency,
        search=search,
        sort_by=effective_sort_by,
        sort_order=effective_sort_order,
    )

    serialized_items = [ChallengeResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        success=True,
        data=serialized_items,
        items=serialized_items,
        pagination=PaginationMetadata(
            page=page,
            page_size=effective_limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/my-submissions",
    response_model=PaginatedResponse[ChallengeResponse],
    status_code=status.HTTP_200_OK,
    summary="List My Submissions",
    description="Lists challenges submitted by the authenticated user with pagination and optional filters.",
)
def list_my_submissions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Frontend alias for page_size"),
    district: Optional[str] = Query(None, description="Filter by district"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Keyword search in user's challenges"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort direction ('asc' or 'desc')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> PaginatedResponse[ChallengeResponse]:
    """Retrieve challenges submitted by current authenticated user."""
    effective_limit = limit or page_size or 20

    items, total, total_pages = challenge_service.list_user_challenges(
        db=db,
        current_user=current_user,
        page=page,
        page_size=effective_limit,
        district=district,
        domain=domain,
        status=status_filter,
        search=search,
        sort_by=sort_by or "created_at",
        sort_order=sort_order or "desc",
    )

    serialized_items = [ChallengeResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        success=True,
        data=serialized_items,
        items=serialized_items,
        pagination=PaginationMetadata(
            page=page,
            page_size=effective_limit,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{challenge_id}",
    response_model=ChallengeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Challenge Details",
    description="Retrieves full details of a specific challenge by its unique UUID.",
)
def get_challenge_detail(
    challenge_id: str,
    db: Session = Depends(get_db),
) -> ChallengeDetailResponse:
    """Retrieve a challenge by its primary key ID."""
    challenge = challenge_service.get_challenge(db, challenge_id)
    return ChallengeDetailResponse.model_validate(challenge)


@router.patch(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Challenge",
    description="Updates challenge content. Only permitted for the original submitter prior to official review lock.",
)
def update_challenge(
    challenge_id: str,
    payload: ChallengeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ChallengeResponse:
    """Update challenge details before review begins."""
    updated = challenge_service.update_challenge(db, challenge_id, payload, current_user)
    return ChallengeResponse.model_validate(updated)


@router.delete(
    "/{challenge_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Challenge",
    description="Deletes an intake challenge. Restricted to submitter prior to official review commencement.",
)
def delete_challenge(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Withdraw and delete challenge record before review begins."""
    challenge_service.delete_challenge(db, challenge_id, current_user)
    return ApiResponse(
        success=True,
        message="Challenge deleted successfully.",
        data={"id": challenge_id},
    )


@router.get(
    "/{challenge_id}/ai-analysis",
    summary="Get AI Analysis for Challenge (Frontend Alias)",
    description="Retrieves AI intelligence, domain extraction, and duplicate clustering for a challenge.",
)
def get_challenge_ai_analysis(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(require_authenticated_user),
):
    from app.ai.service import ai_service
    return ai_service.analyze_challenge_by_id(db=db, challenge_id=challenge_id, current_user=current_user)


@router.post(
    "/{challenge_id}/ai-analysis/trigger",
    summary="Trigger AI Analysis for Challenge (Frontend Alias)",
    description="Executes or refreshes AI problem analysis pipeline for a challenge.",
)
def trigger_challenge_ai_analysis(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(require_authenticated_user),
):
    from app.ai.service import ai_service
    return ai_service.analyze_challenge_by_id(db=db, challenge_id=challenge_id, current_user=current_user)
