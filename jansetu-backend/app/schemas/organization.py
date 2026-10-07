"""
Pydantic v2 Schemas for Organization and Organization Membership.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user import UserResponse
from app.utils.constants import (
    JHARKHAND_DISTRICTS,
    get_canonical_district,
    is_valid_district,
)
from app.utils.enums import OrganizationMembershipRole, OrganizationType


class OrganizationBase(BaseModel):
    """Base shared attributes for Organization."""
    name: str = Field(..., min_length=2, max_length=255, description="Unique organization name")
    legal_name: Optional[str] = Field(None, max_length=255, description="Registered legal name")
    organization_type: OrganizationType = Field(..., description="Institutional category")
    description: Optional[str] = Field(None, max_length=2000, description="Brief description")
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    website: Optional[str] = Field(None, max_length=255, description="Website URL")
    address: Optional[str] = Field(None, max_length=500, description="Physical address")
    district: Optional[str] = Field(None, description="Jharkhand district")
    state: str = Field(default="Jharkhand", max_length=100, description="State")

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: str) -> str:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Organization name cannot be empty or whitespace.")
            return cleaned
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip().lower()
            return cleaned if cleaned else None
        return v

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if not is_valid_district(v):
            raise ValueError(
                f"District '{v}' is not a recognized Jharkhand district. "
                f"Must be one of the 24 official districts: {', '.join(JHARKHAND_DISTRICTS)}"
            )
        return get_canonical_district(v)


class OrganizationCreateRequest(OrganizationBase):
    """Payload for creating a new organization."""
    pass


class OrganizationUpdateRequest(BaseModel):
    """Payload for updating an existing organization."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    organization_type: Optional[OrganizationType] = None
    description: Optional[str] = Field(None, max_length=2000)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    district: Optional[str] = None
    state: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Organization name cannot be empty or whitespace.")
            return cleaned
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            cleaned = v.strip().lower()
            return cleaned if cleaned else None
        return v

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if not is_valid_district(v):
            raise ValueError(
                f"District '{v}' is not a recognized Jharkhand district. "
                f"Must be one of the 24 official districts: {', '.join(JHARKHAND_DISTRICTS)}"
            )
        return get_canonical_district(v)


class OrganizationResponse(BaseModel):
    """Public organization response representation."""
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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationListResponse(BaseModel):
    """Paginated list of organizations."""
    items: List[OrganizationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OrganizationMembershipCreateRequest(BaseModel):
    """Payload for adding a member to an organization."""
    user_id: str = Field(..., description="Target user ID to add as member")
    membership_role: OrganizationMembershipRole = Field(
        default=OrganizationMembershipRole.MEMBER,
        description="Role within organization (owner, admin, member)",
    )


class OrganizationMembershipUpdateRequest(BaseModel):
    """Payload for updating a member's role or status."""
    membership_role: Optional[OrganizationMembershipRole] = None
    is_active: Optional[bool] = None


class OrganizationMembershipResponse(BaseModel):
    """Representation of an organization membership."""
    id: str
    user_id: str
    organization_id: str
    membership_role: OrganizationMembershipRole
    is_active: bool
    joined_at: datetime
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberListResponse(BaseModel):
    """List response for organization memberships."""
    items: List[OrganizationMembershipResponse]
    total: int
