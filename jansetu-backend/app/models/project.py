import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    DateTime,
    desc,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import ProjectStatus


def generate_project_code() -> str:
    """
    Generates a unique project reference code.
    Format: PRJ-YYYY-XXXXXX (e.g. PRJ-2026-F4C9B1)
    """
    year = datetime.now(timezone.utc).year
    random_hex = secrets.token_hex(3).upper()
    return f"PRJ-{year}-{random_hex}"


class Project(Base):
    """
    Project Workspace Entity.
    Represents an active research, engineering, or societal intervention project
    executed by a university and multidisciplinary roster in response to a challenge.
    """
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
        default=generate_project_code,
    )
    challenge_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("challenge_assignments.id", ondelete="SET NULL"),
        nullable=True,
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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(
            ProjectStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ProjectStatus.CREATED,
        nullable=False,
        index=True,
    )
    created_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    lead_faculty: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    student_lead: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    budget: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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
    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="project",
    )
    assignment: Mapped[Optional["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="project",
    )
    university: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="projects",
        foreign_keys=[university_id],
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="projects",
        foreign_keys=[department_id],
    )
    created_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="projects_created",
        foreign_keys=[created_by_user_id],
    )
    teams: Mapped[list["ProjectTeam"]] = relationship(
        "ProjectTeam",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Milestone.sequence_number",
    )
    partners: Mapped[list["ProjectPartner"]] = relationship(
        "ProjectPartner",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    risks: Mapped[list["ProjectRisk"]] = relationship(
        "ProjectRisk",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["ProjectActivity"]] = relationship(
        "ProjectActivity",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="desc(ProjectActivity.created_at)",
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} code={self.project_code} title='{self.title[:30]}' status={self.status}>"
