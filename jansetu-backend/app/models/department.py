import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.department_capability import department_capabilities


class Department(Base):
    """
    University Department Entity.
    Represents an academic, engineering, or research department within a university.
    """
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
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
        back_populates="departments",
    )
    capabilities: Mapped[List["Capability"]] = relationship(
        "Capability",
        secondary=department_capabilities,
        back_populates="departments",
    )
    assignments: Mapped[List["ChallengeAssignment"]] = relationship(
        "ChallengeAssignment",
        back_populates="department",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="department",
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} org_id={self.organization_id} name='{self.name}'>"
