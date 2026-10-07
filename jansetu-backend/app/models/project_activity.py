import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectActivity(Base):
    """
    Project Activity Timeline Entity.
    Provides an auditable, chronological activity log for all major events inside a project workspace.
    """
    __tablename__ = "project_activities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    related_entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    related_entity_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="activities",
    )
    actor_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[actor_user_id],
    )

    def __repr__(self) -> str:
        return f"<ProjectActivity id={self.id} project_id={self.project_id} type='{self.activity_type}'>"
