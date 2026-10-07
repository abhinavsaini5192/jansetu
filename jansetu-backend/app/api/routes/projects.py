"""
Project Workspace Endpoints.
Provides project workspace creation, inspection, and execution tracking for university teams.
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
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMetadata
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import project_service
from app.utils.enums import ProjectStatus

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Proposal / Workspace",
    description="Initializes an institutional project workspace proposal for a challenge.",
)
def create_project(
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    project = project_service.create_project(
        db=db,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return project_service.serialize_project_response(project)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Projects",
    description="Lists project workspaces with optional filtering by university, challenge, or status.",
)
def list_projects(
    university_id: Optional[str] = Query(None, description="Filter by university ID"),
    challenge_id: Optional[str] = Query(None, description="Filter by challenge ID"),
    status_filter: Optional[ProjectStatus] = Query(None, alias="status", description="Filter by project status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> PaginatedResponse[ProjectResponse]:
    items, total, total_pages = project_service.list_projects(
        db=db,
        university_id=university_id,
        challenge_id=challenge_id,
        status=status_filter,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )
    serialized = [project_service.serialize_project_response(p) for p in items]
    return PaginatedResponse(
        success=True,
        message="Projects retrieved successfully.",
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


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project Details",
    description="Retrieves full project workspace details, multidisciplinary roster, and milestones.",
)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ProjectResponse:
    project = project_service.get_project_by_id(db=db, project_id=project_id, current_user=current_user)
    return project_service.serialize_project_response(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Project Workspace",
)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProjectResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    project = project_service.update_project(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return project_service.serialize_project_response(project)
