from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import SocietalDomain


class CapabilityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    domain: SocietalDomain
    keywords: Optional[str] = None


class CapabilityCreate(CapabilityBase):
    pass


class CapabilityResponse(CapabilityBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    capability_ids: Optional[List[str]] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: str
    organization_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    capabilities: List[CapabilityResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DepartmentCapabilityLink(BaseModel):
    capability_id: str
