"""
Notification Service for JanSetu Platform.
Manages creation, retrieval, and status tracking for in-app user notifications.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union

from sqlalchemy import desc, func, select, update
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.logging_config import logger
from app.models.notification import Notification
from app.models.user import User
from app.utils.enums import NotificationType


class NotificationService:
    """Service handling in-app notifications lifecycle."""

    def create_notification(
        self,
        db: Session,
        recipient_user_id: str,
        notification_type: Union[NotificationType, str],
        title: str,
        message: str,
        related_challenge_id: Optional[str] = None,
        **kwargs,
    ) -> Notification:
        """Creates a new in-app notification for a user."""
        type_str = notification_type.value if isinstance(notification_type, NotificationType) else str(notification_type)

        notification = Notification(
            recipient_user_id=recipient_user_id,
            notification_type=type_str,
            title=title,
            message=message,
            related_challenge_id=related_challenge_id,
            is_read=False,
        )

        try:
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to create notification for user {recipient_user_id}: {e}")
            return notification

    def list_user_notifications(
        self,
        db: Session,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int, int]:
        """
        Lists notifications for the authenticated user, newest first.
        Users can only access their own notifications.
        """
        query = select(Notification).where(Notification.recipient_user_id == current_user.id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        # Count total matching
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        # Unread total count regardless of unread_only filter
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.recipient_user_id == current_user.id,
            Notification.is_read == False,
        )
        unread_count = db.scalar(unread_stmt) or 0

        # Paginated items
        skip = (page - 1) * page_size
        stmt = query.order_by(desc(Notification.created_at)).offset(skip).limit(page_size)
        items = list(db.scalars(stmt).all())

        return items, total, unread_count

    def get_unread_count(self, db: Session, current_user: User) -> int:
        """Returns the total number of unread notifications for a user."""
        stmt = select(func.count(Notification.id)).where(
            Notification.recipient_user_id == current_user.id,
            Notification.is_read == False,
        )
        return db.scalar(stmt) or 0

    def mark_as_read(
        self,
        db: Session,
        notification_id: str,
        current_user: User,
    ) -> Notification:
        """Marks an individual notification as read. Validates user ownership."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise NotFoundException(f"Notification '{notification_id}' not found.")

        if notification.recipient_user_id != current_user.id:
            raise ForbiddenException("You do not have permission to modify this notification.")

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(notification)

        return notification

    def mark_all_as_read(
        self,
        db: Session,
        current_user: User,
    ) -> int:
        """Marks all unread notifications as read for current user. Returns count updated."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(Notification)
            .where(
                Notification.recipient_user_id == current_user.id,
                Notification.is_read == False,
            )
            .values(is_read=True, read_at=now)
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount or 0


notification_service = NotificationService()
