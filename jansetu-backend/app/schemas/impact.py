"""
Pydantic Schemas for Impact Records and Field Evidence (Phases 3.6 & 3.7).
Maintains dual compatibility with Phase 3 specifications and React Screen 09 (9_ImpactDashboard.jsx).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import EvidenceType, EvidenceVerificationStatus, ImpactStatus, ImpactType


class EvidenceCreate(BaseModel):
    title: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    description: Optional[str] = None
    attachment_id: Optional[str] = None
    capture_date: Optional[datetime] = None
    source_reference: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class EvidenceVerificationRequest(BaseModel):
    verification_notes: Optional[str] = None
    decision: str = "VERIFIED"  # VERIFIED | REJECTED | NEEDS_CLARIFICATION


class EvidenceResponse(BaseModel):
    id: str
    impact_record_id: str
    submitted_by_user_id: str
    attachment_id: Optional[str] = None
    title: Optional[str] = None
    evidence_type: str
    description: Optional[str] = None
    capture_date: Optional[datetime] = None
    source_reference: Optional[str] = None
    verification_status: str
    verified_by_user_id: Optional[str] = None
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    file_url: Optional[str] = None
    fileUrl: Optional[str] = None
    isVerified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ImpactCreate(BaseModel):
    title: str = "Verified Societal Impact Assessment"
    description: Optional[str] = None
    impact_type: ImpactType = ImpactType.SOCIAL
    target_population: Optional[str] = None
    actual_beneficiaries: Optional[str] = None
    geographic_coverage: Optional[str] = None
    villages_covered: int = 0
    baseline_value: Optional[str] = None
    achieved_value: Optional[str] = None
    measurement_unit: Optional[str] = None
    outcome_summary: Optional[str] = None
    economic_benefit: Optional[str] = None

    # Frontend Screen 09 Aliases
    villagesCovered: Optional[int] = None
    beneficiariesReached: Optional[str] = None
    baselineMetric: Optional[str] = None
    postInterventionMetric: Optional[str] = None
    economicBenefit: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ImpactUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    impact_type: Optional[ImpactType] = None
    target_population: Optional[str] = None
    actual_beneficiaries: Optional[str] = None
    geographic_coverage: Optional[str] = None
    villages_covered: Optional[int] = None
    baseline_value: Optional[str] = None
    achieved_value: Optional[str] = None
    measurement_unit: Optional[str] = None
    outcome_summary: Optional[str] = None
    economic_benefit: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ImpactVerificationRequest(BaseModel):
    verification_notes: Optional[str] = None
    signatoryNote: Optional[str] = None
    signatory_note: Optional[str] = None
    decision: str = "VERIFIED"  # VERIFIED | REJECTED | NEEDS_CLARIFICATION

    model_config = ConfigDict(populate_by_name=True)


class ImpactResponse(BaseModel):
    id: str
    project_id: str
    challenge_id: Optional[str] = None
    submitted_by_user_id: str
    title: str
    description: Optional[str] = None
    impact_type: str
    target_population: Optional[str] = None
    actual_beneficiaries: Optional[str] = None
    geographic_coverage: Optional[str] = None
    villages_covered: int = 0
    baseline_value: Optional[str] = None
    achieved_value: Optional[str] = None
    measurement_unit: Optional[str] = None
    outcome_summary: Optional[str] = None
    economic_benefit: Optional[str] = None
    status: str
    verification_notes: Optional[str] = None
    verified_by_user_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    evidence_records: List[EvidenceResponse] = Field(default_factory=list)

    # Frontend Screen 09 (9_ImpactDashboard.jsx) Compatibility Fields
    isGovernmentVerified: bool = False
    villagesCovered: int = 0
    beneficiariesReached: Optional[str] = None
    baselineMetric: Optional[str] = None
    postInterventionMetric: Optional[str] = None
    economicBenefit: Optional[str] = None
    verificationSignatory: Optional[str] = None
    chartData: List[Dict[str, Any]] = Field(default_factory=list)
    evidenceDossier: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
