import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import ProposalStatus


class Proposal(Base):
    """
    Project Proposal Entity.
    Represents an institutional solution proposal submitted for an assigned project/challenge.
    """
    __tablename__ = "proposals"

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
    submitted_by_team_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("project_teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    detailed_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    methodology: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    expected_outcomes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    estimated_budget: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    required_resources: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    implementation_timeline: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[ProposalStatus] = mapped_column(
        SQLEnum(
            ProposalStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ProposalStatus.DRAFT,
        nullable=False,
        index=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    review_comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
        back_populates="proposals",
    )
    team: Mapped[Optional["ProjectTeam"]] = relationship(
        "ProjectTeam",
        back_populates="proposals",
        foreign_keys=[submitted_by_team_id],
    )
    reviewed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[reviewed_by_user_id],
    )

    def __repr__(self) -> str:
        return f"<Proposal id={self.id} project_id={self.project_id} title='{self.title[:30]}' status={self.status}>"
