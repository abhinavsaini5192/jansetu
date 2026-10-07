from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.enums import UserRole


class UserBase(BaseModel):
    """Base user attributes."""
    full_name: str = Field(..., min_length=2, max_length=150, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserResponse(UserBase):
    """Public user response schema. Never exposes password hash."""
    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
