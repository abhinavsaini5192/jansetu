from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import RiskLikelihood, RiskSeverity, RiskStatus


class RiskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5, max_length=2000)
    severity: RiskSeverity = Field(default=RiskSeverity.MEDIUM)
    likelihood: RiskLikelihood = Field(default=RiskLikelihood.MEDIUM)
    mitigation_plan: Optional[str] = Field(None, max_length=2000)
    owner_user_id: Optional[str] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    severity: Optional[RiskSeverity] = None
    likelihood: Optional[RiskLikelihood] = None
    mitigation_plan: Optional[str] = None
    owner_user_id: Optional[str] = None
    status: Optional[RiskStatus] = None


class RiskResolveRequest(BaseModel):
    resolution_notes: Optional[str] = Field(None, max_length=1000)


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: str
    severity: RiskSeverity
    likelihood: RiskLikelihood
    risk_score: int
    mitigation_plan: Optional[str] = None
    owner_user_id: Optional[str] = None
    status: RiskStatus
    identified_by_user_id: str
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
