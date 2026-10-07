import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import InstitutionCategory


class UniversityProfile(Base):
    """
    University Profile Entity.
    One-to-one extension of Organization (type=UNIVERSITY) storing academic,
    accreditation, and location-specific metadata for HEI collaboration.
    """
    __tablename__ = "university_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    institution_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    institution_category: Mapped[InstitutionCategory] = mapped_column(
        SQLEnum(
            InstitutionCategory,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=InstitutionCategory.UNIVERSITY,
        nullable=False,
        index=True,
    )
    accreditation_details: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    established_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    official_contact_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    official_website: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    district: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    state: Mapped[str] = mapped_column(
        String(100),
        default="Jharkhand",
        nullable=False,
    )
    pincode: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="university_profile",
    )

    def __repr__(self) -> str:
        return f"<UniversityProfile id={self.id} org_id={self.organization_id} category={self.institution_category}>"
