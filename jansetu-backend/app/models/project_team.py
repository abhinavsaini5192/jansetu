import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectTeam(Base):
    """
    Project Team Entity.
    Represents an active multidisciplinary research or execution team formed under a Project.
    """
    __tablename__ = "project_teams"

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
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
        back_populates="teams",
    )
    members: Mapped[List["ProjectTeamMember"]] = relationship(
        "ProjectTeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    created_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
    )
    proposals: Mapped[List["Proposal"]] = relationship(
        "Proposal",
        back_populates="team",
    )

    def __repr__(self) -> str:
        return f"<ProjectTeam id={self.id} name='{self.name}' project_id={self.project_id}>"
