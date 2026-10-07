"""
Audit Log Database Model for JanSetu Platform.
Stores immutable security, operational, and governance audit records.
Sensitive credentials, passwords, JWT tokens, and secrets are strictly excluded.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    """
    Audit Log Entity.
    Immutable log record tracking critical events across user authentication,
    challenge operations, file attachments, and government reviews.
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    actor_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    actor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[actor_user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} actor={self.actor_user_id} action={self.action} "
            f"entity={self.entity_type}:{self.entity_id}>"
        )
