"""
Evidence Record Entity Model (Phase 3.7).
Connects field photos, lab reports, surveys, and documents to verified impact outcomes.
"""
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import EvidenceType, EvidenceVerificationStatus


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    impact_record_id = Column(String(36), ForeignKey("impact_records.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    attachment_id = Column(String(36), ForeignKey("attachments.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=True)
    evidence_type = Column(
        Enum(EvidenceType, name="evidence_type", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EvidenceType.DOCUMENT,
    )
    description = Column(Text, nullable=True)
    capture_date = Column(DateTime(timezone=True), nullable=True)
    source_reference = Column(String(255), nullable=True)

    verification_status = Column(
        Enum(EvidenceVerificationStatus, name="evidence_verification_status", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EvidenceVerificationStatus.PENDING,
        index=True,
    )
    verified_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    impact_record = relationship("ImpactRecord", back_populates="evidence_records")
    attachment = relationship("Attachment")
    submitted_by = relationship("User", foreign_keys=[submitted_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])
