"""
Impact Record Entity Model (Phase 3.6).
Captures verified on-ground outcomes, beneficiary metrics, and government attestations
distinct from project completion.
"""
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.utils.enums import ImpactStatus, ImpactType


class ImpactRecord(Base):
    __tablename__ = "impact_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = Column(String(36), ForeignKey("challenges.id", ondelete="SET NULL"), nullable=True, index=True)
    submitted_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    impact_type = Column(
        Enum(ImpactType, name="impact_type", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ImpactType.SOCIAL,
    )
    target_population = Column(String(255), nullable=True)
    actual_beneficiaries = Column(String(255), nullable=True)
    geographic_coverage = Column(String(255), nullable=True)
    villages_covered = Column(Integer, default=0, nullable=False)
    baseline_value = Column(String(255), nullable=True)
    achieved_value = Column(String(255), nullable=True)
    measurement_unit = Column(String(100), nullable=True)
    outcome_summary = Column(Text, nullable=True)
    economic_benefit = Column(String(255), nullable=True)

    status = Column(
        Enum(ImpactStatus, name="impact_status", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ImpactStatus.DRAFT,
        index=True,
    )
    verification_notes = Column(Text, nullable=True)
    verified_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", backref="impact_records")
    challenge = relationship("Challenge", backref="impact_records")
    submitted_by = relationship("User", foreign_keys=[submitted_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])
    evidence_records = relationship("EvidenceRecord", back_populates="impact_record", cascade="all, delete-orphan")
