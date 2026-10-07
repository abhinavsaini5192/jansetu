import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import MilestoneStatus


class Milestone(Base):
    """
    Project Milestone Entity.
    Tracks execution checkpoints, planned and actual timelines, and completion metrics.
    """
    __tablename__ = "milestones"

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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    sequence_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    planned_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    planned_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[MilestoneStatus] = mapped_column(
        SQLEnum(
            MilestoneStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=MilestoneStatus.NOT_STARTED,
        nullable=False,
        index=True,
    )
    completion_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    created_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="milestones",
    )
    deliverables: Mapped[List["Deliverable"]] = relationship(
        "Deliverable",
        back_populates="milestone",
        cascade="all, delete-orphan",
    )
    created_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
    )

    def __repr__(self) -> str:
        return f"<Milestone id={self.id} project_id={self.project_id} seq={self.sequence_number} status={self.status}>"
