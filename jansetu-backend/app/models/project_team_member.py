import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import TeamRole


class ProjectTeamMember(Base):
    """
    Project Team Member Association Entity.
    Links individual users (faculty mentor, student lead, researcher) to a project team.
    """
    __tablename__ = "project_team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_project_team_member_team_user"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    team_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[TeamRole] = mapped_column(
        SQLEnum(
            TeamRole,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=TeamRole.STUDENT,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
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
    team: Mapped["ProjectTeam"] = relationship(
        "ProjectTeam",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
    )

    def __repr__(self) -> str:
        return f"<ProjectTeamMember id={self.id} team_id={self.team_id} user_id={self.user_id} role={self.role}>"
