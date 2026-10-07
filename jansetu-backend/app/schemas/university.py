from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.utils.enums import InstitutionCategory, OrganizationType


class UniversityProfileBase(BaseModel):
    institution_code: Optional[str] = None
    institution_category: InstitutionCategory = InstitutionCategory.UNIVERSITY
    accreditation_details: Optional[str] = None
    established_year: Optional[int] = None
    official_contact_email: Optional[str] = None
    official_website: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: str = "Jharkhand"
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UniversityProfileCreate(UniversityProfileBase):
    pass


class UniversityProfileUpdate(BaseModel):
    institution_code: Optional[str] = None
    institution_category: Optional[InstitutionCategory] = None
    accreditation_details: Optional[str] = None
    established_year: Optional[int] = None
    official_contact_email: Optional[str] = None
    official_website: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


class UniversityProfileResponse(UniversityProfileBase):
    id: str
    organization_id: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UniversityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: str = "Jharkhand"
    profile: Optional[UniversityProfileCreate] = None


class UniversityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    legal_name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    is_active: Optional[bool] = None
    profile: Optional[UniversityProfileUpdate] = None


class UniversityVerificationUpdate(BaseModel):
    is_verified: bool
    notes: Optional[str] = None


class UniversityResponse(BaseModel):
    id: str
    name: str
    legal_name: Optional[str] = None
    organization_type: OrganizationType
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: str
    is_active: bool
    is_verified: bool
    profile: Optional[UniversityProfileResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
