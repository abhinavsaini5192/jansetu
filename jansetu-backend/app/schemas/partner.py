from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import PartnerStatus, PartnerType, SupportStatus, SupportType


class SupportOfferCreate(BaseModel):
    support_type: SupportType = Field(default=SupportType.FUNDING)
    description: str = Field(..., min_length=5, max_length=2000)
    estimated_value: Optional[str] = Field(None, max_length=100, description="Declared estimate (unverified)")


class SupportOfferUpdate(BaseModel):
    support_type: Optional[SupportType] = None
    description: Optional[str] = None
    estimated_value: Optional[str] = None
    status: Optional[SupportStatus] = None


class SupportOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_partner_id: str
    support_type: SupportType
    description: str
    estimated_value: Optional[str] = None
    status: SupportStatus
    created_at: datetime
    updated_at: datetime


class PartnerInviteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    organization_id: Optional[str] = Field(None, description="Target partner organization ID")
    partner_id: Optional[str] = Field(None, description="Frontend alias for organization_id")
    partnerId: Optional[str] = Field(None, description="Frontend camelCase alias for organization_id")
    partner_type: Optional[PartnerType] = Field(default=PartnerType.INDUSTRY)
    supportType: Optional[str] = Field(None, description="Frontend supportType string")
    support_type: Optional[str] = Field(None, description="Support type string")
    invitation_message: Optional[str] = Field(None, max_length=2000)


class PartnerResponseRequest(BaseModel):
    decision: str = Field(..., pattern="^(accept|decline)$")
    response_message: Optional[str] = Field(None, max_length=2000)


class PartnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    organization_id: str
    organization_name: Optional[str] = None
    partner_type: PartnerType
    status: PartnerStatus
    invited_by_user_id: str
    invitation_message: Optional[str] = None
    response_message: Optional[str] = None
    joined_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    support_offers: List[SupportOfferResponse] = []
