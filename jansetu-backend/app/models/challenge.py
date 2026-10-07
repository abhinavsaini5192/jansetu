"""
Challenge Database Model for JanSetu Platform.
Represents societal issues and community problems submitted by citizens,
community organizations, NGOs, and authorized users.
"""
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import (
    ChallengeStatus,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    ValidationStatus,
)


def generate_challenge_reference_code() -> str:
    """
    Generates a unique, collision-resistant, human-readable challenge reference code.
    Format: JS-YYYY-XXXXXX (e.g. JS-2026-A3F8B2)
    """
    year = datetime.now(timezone.utc).year
    random_hex = secrets.token_hex(3).upper()
    return f"JS-{year}-{random_hex}"


class Challenge(Base):
    """
    Societal Challenge Entity.
    Intake record capturing grassroots societal problems for verification,
    categorization, institution assignment, and collaborative innovation.
    """
    __tablename__ = "challenges"

    # Identity
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    reference_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
        default=generate_challenge_reference_code,
    )

    # Submitter Relationships
    submitted_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    submitted_by_organization_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Basic Information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    title_hi: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    problem_statement: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    proposed_context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Location Information
    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    block: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    village_or_ward: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    location_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Classification & Prioritization
    domain: Mapped[SocietalDomain] = mapped_column(
        SQLEnum(
            SocietalDomain,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
    )
    subdomain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        SQLEnum(
            PriorityLevel,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=PriorityLevel.MEDIUM,
        nullable=False,
        index=True,
    )
    urgency: Mapped[UrgencyLevel] = mapped_column(
        SQLEnum(
            UrgencyLevel,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=UrgencyLevel.MEDIUM,
        nullable=False,
        index=True,
    )

    # Workflow & Review State
    status: Mapped[ChallengeStatus] = mapped_column(
        SQLEnum(
            ChallengeStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ChallengeStatus.SUBMITTED,
        nullable=False,
        index=True,
    )
    validation_status: Mapped[ValidationStatus] = mapped_column(
        SQLEnum(
            ValidationStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ValidationStatus.PENDING,
        nullable=False,
        index=True,
    )
    assigned_department: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Impact & Contextual Metadata
    affected_population: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    estimated_beneficiaries: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    existing_attempts: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    expected_outcome: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    constraints: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Lifecycle Timestamps
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
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

    # Future-Compatible Governance Flags
    validated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duplicate_of_challenge_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ORM Relationships
    submitted_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[submitted_by_user_id],
        back_populates="challenges",
    )
    submitted_by_organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[submitted_by_organization_id],
        back_populates="challenges",
    )
    duplicate_of: Mapped[Optional["Challenge"]] = relationship(
        "Challenge",
        remote_side=[id],
        foreign_keys=[duplicate_of_challenge_id],
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["GovernmentReview"]] = relationship(
        "GovernmentReview",
        back_populates="challenge",
        cascade="all, delete-orphan",
        foreign_keys="GovernmentReview.challenge_id",
    )
    assignments: Mapped[list["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="challenge",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Challenge id={self.id} ref={self.reference_code} title='{self.title[:30]}' status={self.status}>"
