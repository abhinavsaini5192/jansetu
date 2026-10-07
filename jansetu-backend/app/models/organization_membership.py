import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import OrganizationMembershipRole


class OrganizationMembership(Base):
    """
    Organization Membership Association Entity.
    Links Users to Organizations with institution-scoped roles (Owner, Admin, Member).
    """
    __tablename__ = "organization_memberships"

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization_membership"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    membership_role: Mapped[OrganizationMembershipRole] = mapped_column(
        SQLEnum(
            OrganizationMembershipRole,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=OrganizationMembershipRole.MEMBER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="memberships",
    )

    def __repr__(self) -> str:
        return f"<OrganizationMembership user={self.user_id} org={self.organization_id} role={self.membership_role}>"
