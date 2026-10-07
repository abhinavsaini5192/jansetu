"""
In-App Notifications API Routes.
Provides endpoints for users to list alerts, check unread counts,
and mark notifications as read.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.notification_service import notification_service

router = APIRouter()


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List User Notifications",
    description="Retrieves in-app notifications for the authenticated user with optional unread filter.",
)
def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Frontend alias for page_size"),
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> NotificationListResponse:
    """List notifications for caller."""
    effective_limit = limit or page_size or 20
    items, total, unread_count = notification_service.list_user_notifications(
        db=db,
        current_user=current_user,
        page=page,
        page_size=effective_limit,
        unread_only=unread_only,
    )
    serialized = [NotificationResponse.model_validate(item) for item in items]
    return NotificationListResponse(
        items=serialized,
        total=total,
        unread_count=unread_count,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Unread Notification Count",
    description="Quick counter for dashboard badge indicators.",
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> UnreadCountResponse:
    """Return count of unread notifications."""
    count = notification_service.get_unread_count(db, current_user)
    return UnreadCountResponse(unread_count=count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Notification as Read",
)
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> NotificationResponse:
    """Mark single notification as read."""
    updated = notification_service.mark_as_read(db, notification_id, current_user)
    return NotificationResponse.model_validate(updated)


@router.patch(
    "/read-all",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Mark All Notifications as Read",
)
@router.post(
    "/read-all",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Mark All Notifications as Read (POST alias)",
    include_in_schema=False,
)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Mark all unread notifications as read."""
    updated_count = notification_service.mark_all_as_read(db, current_user)
    return ApiResponse(
        success=True,
        message="All notifications marked as read.",
        data={"updated_count": updated_count},
    )
