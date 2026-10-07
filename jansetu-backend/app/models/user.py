import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import UserRole


class User(Base):
    """
    User Database Entity.
    Represents platform actors including citizens, nodal officers, faculty, and administrators.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.CITIZEN,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    memberships: Mapped[List["OrganizationMembership"]] = relationship(
        "OrganizationMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    challenges: Mapped[List["Challenge"]] = relationship(
        "Challenge",
        back_populates="submitted_by_user",
        foreign_keys="Challenge.submitted_by_user_id",
    )
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="uploaded_by_user",
        foreign_keys="Attachment.uploaded_by_user_id",
    )
    government_reviews: Mapped[List["GovernmentReview"]] = relationship(
        "GovernmentReview",
        back_populates="reviewer_user",
        foreign_keys="GovernmentReview.reviewer_user_id",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="recipient",
        cascade="all, delete-orphan",
        foreign_keys="Notification.recipient_user_id",
    )
    assignments_issued: Mapped[List["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="assigned_by_user",
        foreign_keys="ChallengeAssignment.assigned_by_user_id",
    )
    projects_created: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="created_by_user",
        foreign_keys="Project.created_by_user_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"

