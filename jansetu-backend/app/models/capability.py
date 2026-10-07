import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.department_capability import department_capabilities
from app.utils.enums import SocietalDomain


class Capability(Base):
    """
    Institutional Capability Entity.
    Represents domain expertise, specialized labs, technology competencies,
    or research tracks registered by universities and academic departments.
    """
    __tablename__ = "capabilities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    domain: Mapped[SocietalDomain] = mapped_column(
        SQLEnum(
            SocietalDomain,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
    )
    keywords: Mapped[Optional[str]] = mapped_column(
        String(500),
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

    # Relationships
    departments: Mapped[List["Department"]] = relationship(
        "Department",
        secondary=department_capabilities,
        back_populates="capabilities",
    )

    def __repr__(self) -> str:
        return f"<Capability id={self.id} name='{self.name}' domain={self.domain}>"
