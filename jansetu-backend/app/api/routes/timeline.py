"""
Project Activity Timeline Endpoints.
Phase 2.10: Chronological audit trail and timeline of project workspace events.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.project_activity import ProjectActivity
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.services.project_activity_service import project_activity_service

router = APIRouter()


def serialize_activity(activity: ProjectActivity) -> ActivityResponse:
    actor_name = activity.actor_user.full_name if activity.actor_user else "System"
    return ActivityResponse(
        id=activity.id,
        project_id=activity.project_id,
        actor_user_id=activity.actor_user_id,
        actor_name=actor_name,
        activity_type=activity.activity_type,
        title=activity.title,
        description=activity.description,
        related_entity_type=activity.related_entity_type,
        related_entity_id=activity.related_entity_id,
        metadata_json=activity.metadata_json,
        created_at=activity.created_at,
    )


@router.get(
    "/projects/{project_id}/timeline",
    response_model=PaginatedResponse[ActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Project Activity Timeline",
    description="Returns an auditable, paginated chronological log of all actions taken in the project workspace.",
)
def get_project_timeline(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[ActivityResponse]:
    items, total, total_pages = project_activity_service.list_project_timeline(
        db=db,
        project_id=project_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
        activity_type=activity_type,
    )
    serialized = [serialize_activity(a) for a in items]
    return PaginatedResponse(
        success=True,
        message="Project activity timeline retrieved successfully.",
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
