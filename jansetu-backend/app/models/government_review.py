"""
Government Review Database Model for JanSetu Platform.
Stores official human-authorized evaluations and decisions made by government
nodal officers and platform administrators on societal challenges.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GovernmentReview(Base):
    """
    Government Review Entity.
    Maintains an audit trail of administrative verification decisions:
    validations, rejections, duplicate designations, and clarification requests.
    """
    __tablename__ = "government_reviews"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    challenge_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    previous_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    validation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    review_comment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    duplicate_of_challenge_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("challenges.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    clarification_request: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    reviewed_at: Mapped[datetime] = mapped_column(
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

    # Relationships
    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="reviews",
        foreign_keys=[challenge_id],
    )
    reviewer_user: Mapped["User"] = relationship(
        "User",
        back_populates="government_reviews",
        foreign_keys=[reviewer_user_id],
    )
    duplicate_of_challenge: Mapped[Optional["Challenge"]] = relationship(
        "Challenge",
        foreign_keys=[duplicate_of_challenge_id],
    )

    def __repr__(self) -> str:
        return (
            f"<GovernmentReview id={self.id} challenge_id={self.challenge_id} "
            f"reviewer={self.reviewer_user_id} status='{self.previous_status}'->'{self.new_status}'>"
        )
