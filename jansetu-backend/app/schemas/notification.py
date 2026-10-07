"""
Pydantic v2 Schemas for In-App Notifications.
Defines public contracts for alerts delivered to citizens, institutions,
and government officers.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """Public representation of an in-app notification item."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_user_id: str
    notification_type: str
    title: str
    message: str
    related_challenge_id: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    """Paginated listing of user notifications with unread counter."""
    items: List[NotificationResponse] = Field(default_factory=list)
    total: int = 0
    unread_count: int = 0


class UnreadCountResponse(BaseModel):
    """Simple response providing count of unread notifications."""
    unread_count: int = 0
