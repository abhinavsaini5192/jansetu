import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import DeliverableStatus


class Deliverable(Base):
    """
    Milestone Deliverable Entity.
    Represents an evidence document, code artifact, or demonstration report tied to a milestone.
    """
    __tablename__ = "deliverables"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    milestone_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    file_attachment_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("attachments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    submitted_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[DeliverableStatus] = mapped_column(
        SQLEnum(
            DeliverableStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=DeliverableStatus.PENDING,
        nullable=False,
        index=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    review_comment: Mapped[Optional[str]] = mapped_column(
        Text,
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
    milestone: Mapped["Milestone"] = relationship(
        "Milestone",
        back_populates="deliverables",
    )
    attachment: Mapped[Optional["Attachment"]] = relationship(
        "Attachment",
        foreign_keys=[file_attachment_id],
    )
    submitted_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[submitted_by_user_id],
    )
    reviewed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[reviewed_by_user_id],
    )

    def __repr__(self) -> str:
        return f"<Deliverable id={self.id} milestone_id={self.milestone_id} title='{self.title[:30]}' status={self.status}>"
