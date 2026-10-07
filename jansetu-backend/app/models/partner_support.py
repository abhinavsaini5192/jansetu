import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import SupportStatus, SupportType


class PartnerSupport(Base):
    """
    Partner Support Commitment Entity.
    Tracks resource contributions (grants, edge hardware, faculty mentorship, field trials)
    provided by corporate, CSR, startup, or NGO partners.
    Financial values represent declared estimates, not platform-cleared payments.
    """
    __tablename__ = "partner_support"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_partner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    support_type: Mapped[SupportType] = mapped_column(
        SQLEnum(
            SupportType,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=SupportType.FUNDING,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    estimated_value: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    status: Mapped[SupportStatus] = mapped_column(
        SQLEnum(
            SupportStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=SupportStatus.PROPOSED,
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
    partner: Mapped["ProjectPartner"] = relationship(
        "ProjectPartner",
        back_populates="support_offers",
    )

    def __repr__(self) -> str:
        return f"<PartnerSupport id={self.id} partner_id={self.project_partner_id} type={self.support_type} status={self.status}>"
