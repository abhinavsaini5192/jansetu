"""
Notification Database Model for JanSetu Platform.
Stores persistent in-app notifications for users regarding challenge verification,
administrative reviews, and important platform updates.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import NotificationType


class Notification(Base):
    """
    In-app Notification Entity.
    Stores notifications delivered to citizens, organization leaders, and government officers.
    """
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    recipient_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        default=NotificationType.GENERAL.value,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    related_challenge_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[recipient_user_id],
    )
    related_challenge: Mapped[Optional["Challenge"]] = relationship(
        "Challenge",
        foreign_keys=[related_challenge_id],
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} recipient={self.recipient_user_id} title='{self.title}' is_read={self.is_read}>"
