"""
University Directory and Institutional Management Endpoints.
Provides university discovery, profile management, verification, and department listings.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    get_current_user_optional,
)
from app.models.user import User
from app.schemas.assignment import AssignmentResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMetadata
from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.schemas.project import ProjectResponse
from app.schemas.university import (
    UniversityCreate,
    UniversityProfileResponse,
    UniversityResponse,
    UniversityUpdate,
    UniversityVerificationUpdate,
)
from app.services.assignment_service import assignment_service
from app.services.department_service import department_service
from app.services.project_service import project_service
from app.services.university_service import university_service
from app.utils.enums import InstitutionCategory

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[UniversityResponse],
    status_code=status.HTTP_200_OK,
    summary="List Universities",
    description="Lists accredited higher education institutions with optional filtering by district, category, or search.",
)
def list_universities(
    search: Optional[str] = Query(None, description="Keyword search"),
    district: Optional[str] = Query(None, description="Filter by Jharkhand district"),
    category: Optional[InstitutionCategory] = Query(None, description="Filter by HEI category"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> PaginatedResponse[UniversityResponse]:
    items, total, total_pages = university_service.list_universities(
        db=db,
        search=search,
        district=district,
        category=category,
        is_verified=is_verified,
        is_active=is_active,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )
    serialized = [UniversityResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        success=True,
        message="Universities retrieved successfully.",
        data=serialized,
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )


@router.post(
    "",
    response_model=ApiResponse[UniversityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register University",
    description="Registers a higher education institution with academic profile.",
)
def create_university(
    payload: UniversityCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[UniversityResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    org = university_service.create_university(
        db=db,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="University registered successfully.",
        data=UniversityResponse.model_validate(org),
    )


@router.get(
    "/{university_id}",
    response_model=ApiResponse[UniversityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get University Details",
)
def get_university(
    university_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[UniversityResponse]:
    org = university_service.get_university_by_id(db=db, university_id=university_id, current_user=current_user)
    return ApiResponse(
        success=True,
        message="University details retrieved.",
        data=UniversityResponse.model_validate(org),
    )


@router.patch(
    "/{university_id}",
    response_model=ApiResponse[UniversityResponse],
    status_code=status.HTTP_200_OK,
    summary="Update University Profile",
)
def update_university(
    university_id: str,
    payload: UniversityUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[UniversityResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    org = university_service.update_university(
        db=db,
        university_id=university_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="University updated successfully.",
        data=UniversityResponse.model_validate(org),
    )


@router.get(
    "/{university_id}/profile",
    response_model=ApiResponse[UniversityProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get University Academic Profile",
)
def get_university_profile(
    university_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[UniversityProfileResponse]:
    org = university_service.get_university_by_id(db=db, university_id=university_id, current_user=current_user)
    if not org.university_profile:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("University profile does not exist.")
    return ApiResponse(
        success=True,
        message="University profile retrieved.",
        data=UniversityProfileResponse.model_validate(org.university_profile),
    )


@router.patch(
    "/{university_id}/verify",
    response_model=ApiResponse[UniversityResponse],
    status_code=status.HTTP_200_OK,
    summary="Verify University",
    description="Authorized platform or government admin marks university as verified.",
)
def verify_university(
    university_id: str,
    payload: UniversityVerificationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[UniversityResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    org = university_service.verify_university(
        db=db,
        university_id=university_id,
        verify_req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="University verification status updated.",
        data=UniversityResponse.model_validate(org),
    )


@router.get(
    "/{university_id}/departments",
    response_model=ApiResponse[List[DepartmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List University Departments",
)
def list_departments_for_university(
    university_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[List[DepartmentResponse]]:
    depts = department_service.list_university_departments(
        db=db,
        university_id=university_id,
        current_user=current_user,
    )
    return ApiResponse(
        success=True,
        message="Departments retrieved successfully.",
        data=[DepartmentResponse.model_validate(d) for d in depts],
    )


@router.post(
    "/{university_id}/departments",
    response_model=ApiResponse[DepartmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create University Department",
)
def create_department_for_university(
    university_id: str,
    payload: DepartmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[DepartmentResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    dept = department_service.create_department(
        db=db,
        university_id=university_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Department created successfully.",
        data=DepartmentResponse.model_validate(dept),
    )


@router.get(
    "/{university_id}/assignments",
    response_model=ApiResponse[List[AssignmentResponse]],
    status_code=status.HTTP_200_OK,
    summary="List University Assignments",
)
def list_university_assignments(
    university_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[List[AssignmentResponse]]:
    assignments = assignment_service.list_assignments_for_university(db=db, university_id=university_id)
    return ApiResponse(
        success=True,
        message="University assignments retrieved.",
        data=[assignment_service.serialize_assignment_response(a) for a in assignments],
    )


@router.get(
    "/{university_id}/projects",
    response_model=ApiResponse[List[ProjectResponse]],
    status_code=status.HTTP_200_OK,
    summary="List University Projects",
)
def list_university_projects(
    university_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[List[ProjectResponse]]:
    projects, _, _ = project_service.list_projects(db=db, university_id=university_id, current_user=current_user)
    return ApiResponse(
        success=True,
        message="University projects retrieved.",
        data=[project_service.serialize_project_response(p) for p in projects],
    )
