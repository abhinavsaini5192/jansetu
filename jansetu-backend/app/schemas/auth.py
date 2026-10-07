from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserBase, UserResponse
from app.utils.enums import UserRole

# Roles permitted for public self-registration
ALLOWED_SELF_REGISTER_ROLES = {
    UserRole.CITIZEN,
    UserRole.COMMUNITY_ORGANIZATION,
    UserRole.STUDENT,
    UserRole.RESEARCHER,
    UserRole.FACULTY,
    UserRole.INDUSTRY_PARTNER,
    UserRole.CSR_PARTNER,
}

# Administrative privileged roles that must be assigned securely by an admin
PRIVILEGED_ROLES = {
    UserRole.PLATFORM_ADMIN,
    UserRole.GOVERNMENT_ADMIN,
    UserRole.DISTRICT_NODAL_OFFICER,
    UserRole.UNIVERSITY_ADMIN,
}


class UserRegisterRequest(UserBase):
    """Payload for public user self-registration."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password must be between 8 and 72 characters",
    )
    role: Optional[UserRole] = Field(
        default=UserRole.CITIZEN,
        description="Desired platform role (defaults to citizen)",
    )

    @field_validator("role", mode="before")
    @classmethod
    def validate_self_registration_role(cls, v: Optional[UserRole]) -> UserRole:
        if v is None:
            return UserRole.CITIZEN

        # Normalize string if needed
        if isinstance(v, str):
            v_lower = v.strip().lower()
            try:
                v = UserRole(v_lower)
            except ValueError:
                raise ValueError(f"Invalid user role: {v}")

        if v in PRIVILEGED_ROLES:
            raise ValueError(
                f"Self-registration for privileged role '{v.value}' is not permitted. "
                "Administrative roles must be provisioned by a platform administrator."
            )

        return v


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class TokenResponse(BaseModel):
    """
    Standard JWT authentication response.
    Includes dual token keys (access_token & token) and nested user profile for
    complete frontend contract compatibility.
    """
    access_token: str
    token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600
