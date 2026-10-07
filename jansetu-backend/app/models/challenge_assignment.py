import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import AssignmentStatus


class ChallengeAssignment(Base):
    """
    Challenge Assignment / Institutional Mandate Entity.
    Tracks the lifecycle of issuing a challenge assignment to a university,
    their acceptance or decline, and linkage to the resulting project workspace.
    """
    __tablename__ = "challenge_assignments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    challenge_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    university_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        SQLEnum(
            AssignmentStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=AssignmentStatus.INVITED,
        nullable=False,
        index=True,
    )
    invitation_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    response_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="assignments",
    )
    university: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="assignments",
        foreign_keys=[university_id],
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="assignments",
        foreign_keys=[department_id],
    )
    assigned_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="assignments_issued",
        foreign_keys=[assigned_by_user_id],
    )
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="assignment",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<ChallengeAssignment id={self.id} challenge_id={self.challenge_id} university_id={self.university_id} status={self.status}>"
