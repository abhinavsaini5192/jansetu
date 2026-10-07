import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import PartnerStatus, PartnerType


class ProjectPartner(Base):
    """
    Project Partner Collaboration Entity.
    Links an external corporate, CSR, startup, or NGO partner to a project workspace.
    """
    __tablename__ = "project_partners"
    __table_args__ = (
        UniqueConstraint("project_id", "organization_id", name="uq_project_partner_project_org"),
    )

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
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partner_type: Mapped[PartnerType] = mapped_column(
        SQLEnum(
            PartnerType,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=PartnerType.INDUSTRY,
        nullable=False,
        index=True,
    )
    status: Mapped[PartnerStatus] = mapped_column(
        SQLEnum(
            PartnerStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=PartnerStatus.INVITED,
        nullable=False,
        index=True,
    )
    invited_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
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
    joined_at: Mapped[Optional[datetime]] = mapped_column(
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
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="partners",
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )
    invited_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by_user_id],
    )
    support_offers: Mapped[List["PartnerSupport"]] = relationship(
        "PartnerSupport",
        back_populates="partner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ProjectPartner id={self.id} project_id={self.project_id} org_id={self.organization_id} status={self.status}>"
