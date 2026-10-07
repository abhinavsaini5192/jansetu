import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import OrganizationType


class Organization(Base):
    """
    Organization Entity.
    Represents external collaborating institutions: government departments,
    universities, industries, NGOs, startups, and community groups.
    """
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    legal_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    organization_type: Mapped[OrganizationType] = mapped_column(
        SQLEnum(
            OrganizationType,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(255),
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
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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
    memberships: Mapped[List["OrganizationMembership"]] = relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    challenges: Mapped[List["Challenge"]] = relationship(
        "Challenge",
        back_populates="submitted_by_organization",
        foreign_keys="Challenge.submitted_by_organization_id",
    )
    university_profile: Mapped[Optional["UniversityProfile"]] = relationship(
        "UniversityProfile",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan",
    )
    departments: Mapped[List["Department"]] = relationship(
        "Department",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    assignments: Mapped[List["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="university",
        foreign_keys="ChallengeAssignment.university_id",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="university",
        foreign_keys="Project.university_id",
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name} type={self.organization_type}>"
