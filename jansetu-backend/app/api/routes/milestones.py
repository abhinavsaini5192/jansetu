"""
Project Milestones & Deliverables Endpoints.
Phase 2.8: Milestone scheduling, progress tracking, deliverable submissions with attachments, and review.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
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
from app.services.milestone_service import milestone_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Project-Scoped Milestone Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/projects/{project_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Milestone",
    description="Adds a scheduled milestone with targets and completion percentage.",
)
def create_milestone(
    project_id: str,
    payload: MilestoneCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MilestoneResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    milestone = milestone_service.create_milestone(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_milestone_response(milestone)


@router.get(
    "/projects/{project_id}/milestones",
    response_model=List[MilestoneResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Milestones",
)
def list_project_milestones(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[MilestoneResponse]:
    milestones = milestone_service.list_milestones(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return [milestone_service.serialize_milestone_response(m) for m in milestones]


@router.patch(
    "/projects/{project_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
    summary="Update Milestone (Frontend Alias)",
)
def update_project_milestone_alias(
    project_id: str,
    milestone_id: str,
    payload: MilestoneUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MilestoneResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    milestone = milestone_service.update_milestone(
        db=db,
        milestone_id=milestone_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_milestone_response(milestone)


# ---------------------------------------------------------------------------
# Individual Milestone Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Milestone Details",
)
def get_milestone(
    milestone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MilestoneResponse:
    milestone = milestone_service.get_milestone(
        db=db,
        milestone_id=milestone_id,
        current_user=current_user,
    )
    return milestone_service.serialize_milestone_response(milestone)


@router.patch(
    "/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Milestone",
    description="Updates milestone dates, description, or progress percentage.",
)
def update_milestone(
    milestone_id: str,
    payload: MilestoneUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MilestoneResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    milestone = milestone_service.update_milestone(
        db=db,
        milestone_id=milestone_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_milestone_response(milestone)


@router.post(
    "/milestones/{milestone_id}/status",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Milestone Status & Progress",
)
def update_milestone_status(
    milestone_id: str,
    payload: MilestoneStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MilestoneResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    req = MilestoneUpdate(
        status=payload.status,
        completion_percentage=payload.completion_percentage,
    )
    milestone = milestone_service.update_milestone(
        db=db,
        milestone_id=milestone_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_milestone_response(milestone)


@router.delete(
    "/milestones/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Milestone",
)
def delete_milestone(
    milestone_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    milestone_service.delete_milestone(
        db=db,
        milestone_id=milestone_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Deliverable Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/milestones/{milestone_id}/deliverables",
    response_model=DeliverableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Deliverable",
    description="Submits a milestone deliverable, linking an existing uploaded attachment if available.",
)
def create_deliverable(
    milestone_id: str,
    payload: DeliverableCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeliverableResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    deliverable = milestone_service.create_deliverable(
        db=db,
        milestone_id=milestone_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_deliverable_response(deliverable)


@router.get(
    "/milestones/{milestone_id}/deliverables",
    response_model=List[DeliverableResponse],
    status_code=status.HTTP_200_OK,
    summary="List Milestone Deliverables",
)
def list_deliverables(
    milestone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[DeliverableResponse]:
    deliverables = milestone_service.list_deliverables(
        db=db,
        milestone_id=milestone_id,
        current_user=current_user,
    )
    return [milestone_service.serialize_deliverable_response(d) for d in deliverables]


@router.get(
    "/deliverables/{deliverable_id}",
    response_model=DeliverableResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Deliverable Details",
)
def get_deliverable(
    deliverable_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeliverableResponse:
    deliverable = milestone_service.get_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        current_user=current_user,
    )
    return milestone_service.serialize_deliverable_response(deliverable)


@router.patch(
    "/deliverables/{deliverable_id}",
    response_model=DeliverableResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Deliverable",
)
def update_deliverable(
    deliverable_id: str,
    payload: DeliverableUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeliverableResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    deliverable = milestone_service.update_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_deliverable_response(deliverable)


@router.post(
    "/deliverables/{deliverable_id}/review",
    response_model=DeliverableResponse,
    status_code=status.HTTP_200_OK,
    summary="Review Deliverable",
    description="Faculty mentor or government authority reviews deliverable (accept, reject, request_revision).",
)
def review_deliverable(
    deliverable_id: str,
    payload: DeliverableReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeliverableResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    deliverable = milestone_service.review_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return milestone_service.serialize_deliverable_response(deliverable)
