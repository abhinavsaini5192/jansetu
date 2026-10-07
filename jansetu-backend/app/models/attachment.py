"""
Attachment Database Model for JanSetu Platform.
Stores file metadata for supporting documents, images, and evidence attached to challenges.
Raw binary file data is stored on disk/object storage, never directly in PostgreSQL.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Attachment(Base):
    """
    Challenge Attachment Entity.
    Links uploaded files (images, PDFs, documents) to a specific Challenge.
    """
    __tablename__ = "attachments"

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
    uploaded_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    file_extension: Mapped[str] = mapped_column(
        String(20),
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
        back_populates="attachments",
    )
    uploaded_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="attachments",
    )

    @property
    def download_url(self) -> str:
        return f"/api/v1/attachments/{self.id}/download"

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} challenge={self.challenge_id} filename='{self.original_filename}'>"
