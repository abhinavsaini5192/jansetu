"""
Department and Capability Endpoints.
Handles individual department operations and capability linkage.
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
from app.schemas.common import ApiResponse
from app.schemas.department import (
    CapabilityCreate,
    CapabilityResponse,
    DepartmentCapabilityLink,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import department_service

router = APIRouter()


@router.get(
    "/{department_id}",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Department Details",
)
def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[DepartmentResponse]:
    dept = department_service.get_department_by_id(db=db, department_id=department_id, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Department retrieved.",
        data=DepartmentResponse.model_validate(dept),
    )


@router.patch(
    "/{department_id}",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Department",
)
def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[DepartmentResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    dept = department_service.update_department(
        db=db,
        department_id=department_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Department updated successfully.",
        data=DepartmentResponse.model_validate(dept),
    )


@router.delete(
    "/{department_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Department",
)
def delete_department(
    department_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[dict]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    department_service.delete_department(
        db=db,
        department_id=department_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Department deleted successfully.",
        data={"department_id": department_id},
    )


@router.get(
    "/{department_id}/capabilities",
    response_model=ApiResponse[List[CapabilityResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Department Capabilities",
)
def list_department_capabilities(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[List[CapabilityResponse]]:
    dept = department_service.get_department_by_id(db=db, department_id=department_id, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Capabilities retrieved.",
        data=[CapabilityResponse.model_validate(c) for c in dept.capabilities],
    )


@router.post(
    "/{department_id}/capabilities",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Attach Capability to Department",
)
def link_department_capability(
    department_id: str,
    payload: DepartmentCapabilityLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[DepartmentResponse]:
    dept = department_service.link_capability(
        db=db,
        department_id=department_id,
        capability_id=payload.capability_id,
        current_user=current_user,
    )
    return ApiResponse(
        success=True,
        message="Capability linked to department.",
        data=DepartmentResponse.model_validate(dept),
    )


@router.delete(
    "/{department_id}/capabilities/{capability_id}",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Remove Capability from Department",
)
def unlink_department_capability(
    department_id: str,
    capability_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[DepartmentResponse]:
    dept = department_service.unlink_capability(
        db=db,
        department_id=department_id,
        capability_id=capability_id,
        current_user=current_user,
    )
    return ApiResponse(
        success=True,
        message="Capability removed from department.",
        data=DepartmentResponse.model_validate(dept),
    )


@router.post(
    "/capabilities/create",
    response_model=ApiResponse[CapabilityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Domain Capability",
)
def create_capability(
    payload: CapabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[CapabilityResponse]:
    cap = department_service.create_capability(db=db, req=payload, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Capability registered successfully.",
        data=CapabilityResponse.model_validate(cap),
    )
