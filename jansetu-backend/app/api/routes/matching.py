"""
Explainable Matching & Challenge Assignment Routing.
Provides matching inspection, match refresh, and institutional mandate issuance endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    get_current_user_optional,
)
from app.models.user import User
from app.schemas.assignment import AssignmentCreate, AssignmentResponse
from app.schemas.common import ApiResponse
from app.schemas.matching import MatchingResponse
from app.schemas.project import ProjectResponse
from app.services.assignment_service import assignment_service
from app.services.matching_service import matching_service

router = APIRouter()


@router.get(
    "/{challenge_id}/matches",
    response_model=MatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Explainable University Matches",
    description="Calculates transparent, rule-based institutional recommendations for a validated challenge.",
)
def get_matches_for_challenge(
    challenge_id: str,
    request: Request,
    limit: Optional[int] = None,
    minimum_score: Optional[float] = None,
    district: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> MatchingResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return matching_service.match_universities_for_challenge(
        db=db,
        challenge_id=challenge_id,
        current_user=current_user,
        limit=limit,
        minimum_score=minimum_score,
        district=district,
        domain=domain,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/{challenge_id}/matches/refresh",
    response_model=MatchingResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh University Matches",
    description="Forces re-calculation of institutional matches for the validated challenge.",
)
def refresh_matches_for_challenge(
    challenge_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> MatchingResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return matching_service.match_universities_for_challenge(
        db=db,
        challenge_id=challenge_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/{challenge_id}/assignments",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Issue Challenge Assignment",
    description="Issues an institutional challenge mandate to an accredited university.",
)
def assign_challenge(
    challenge_id: str,
    payload: AssignmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[AssignmentResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    assignment = assignment_service.create_assignment(
        db=db,
        challenge_id=challenge_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Challenge assignment mandate issued successfully.",
        data=assignment_service.serialize_assignment_response(assignment),
    )


@router.post(
    "/{challenge_id}/assign-hei",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Assign Challenge to HEI (Frontend Alias)",
    description="Frontend compatibility endpoint for assigning challenge to Higher Education Institution.",
)
def assign_challenge_hei_alias(
    challenge_id: str,
    payload: AssignmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[AssignmentResponse]:
    return assign_challenge(
        challenge_id=challenge_id,
        payload=payload,
        request=request,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{challenge_id}/assignments",
    response_model=ApiResponse[List[AssignmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Challenge Assignments",
)
def list_challenge_assignments(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[List[AssignmentResponse]]:
    assignments = assignment_service.list_assignments_for_challenge(db=db, challenge_id=challenge_id)
    return ApiResponse(
        success=True,
        message="Challenge assignments retrieved.",
        data=[assignment_service.serialize_assignment_response(a) for a in assignments],
    )


@router.get(
    "/{challenge_id}/project",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project for Challenge",
    description="Retrieves the active project workspace associated with the challenge.",
)
def get_challenge_project(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ProjectResponse:
    from app.services.project_service import project_service
    project = project_service.get_project_by_challenge_id(db=db, challenge_id=challenge_id, current_user=current_user)
    return project_service.serialize_project_response(project)

