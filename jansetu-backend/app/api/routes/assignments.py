"""
Institutional Assignment Lifecycle Decision Endpoints.
Handles mandate acceptance, decline, and cancellation with state machine controls.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.assignment import (
    AssignmentAcceptRequest,
    AssignmentCancelRequest,
    AssignmentDeclineRequest,
    AssignmentResponse,
)
from app.schemas.common import ApiResponse
from app.services.assignment_service import assignment_service

router = APIRouter()


@router.post(
    "/{assignment_id}/accept",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Accept Challenge Mandate",
    description="Authorized university administrator accepts institutional mandate, automatically provisioning a project workspace.",
)
def accept_assignment(
    assignment_id: str,
    payload: Optional[AssignmentAcceptRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[AssignmentResponse]:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or AssignmentAcceptRequest()
    assignment = assignment_service.accept_assignment(
        db=db,
        assignment_id=assignment_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Assignment accepted and project workspace initialized.",
        data=assignment_service.serialize_assignment_response(assignment),
    )


@router.post(
    "/{assignment_id}/decline",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Decline Challenge Mandate",
    description="Authorized university administrator declines institutional mandate.",
)
def decline_assignment(
    assignment_id: str,
    payload: Optional[AssignmentDeclineRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[AssignmentResponse]:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or AssignmentDeclineRequest()
    assignment = assignment_service.decline_assignment(
        db=db,
        assignment_id=assignment_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Assignment declined.",
        data=assignment_service.serialize_assignment_response(assignment),
    )


@router.post(
    "/{assignment_id}/cancel",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel Challenge Assignment",
    description="Authorized government official or platform admin cancels mandate.",
)
def cancel_assignment(
    assignment_id: str,
    payload: Optional[AssignmentCancelRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[AssignmentResponse]:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or AssignmentCancelRequest()
    assignment = assignment_service.cancel_assignment(
        db=db,
        assignment_id=assignment_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Assignment cancelled.",
        data=assignment_service.serialize_assignment_response(assignment),
    )
