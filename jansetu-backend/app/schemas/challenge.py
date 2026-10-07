"""
Pydantic v2 Validation Schemas for Societal Challenges.
Defines input payloads, validation rules, and public response representations
for challenges submitted by citizens, community groups, and NGOs.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.constants import (
    JHARKHAND_DISTRICTS,
    get_canonical_district,
    is_valid_district,
)
from app.utils.enums import (
    ChallengeStatus,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    ValidationStatus,
    normalize_enum_value,
)

# Friendly domain aliases mapping frontend/intake values to canonical SocietalDomain
DOMAIN_ALIASES: Dict[str, SocietalDomain] = {
    "water_sanitation": SocietalDomain.WATER,
    "clean_energy": SocietalDomain.ENERGY,
    "smart_education": SocietalDomain.EDUCATION,
    "waste_management": SocietalDomain.SANITATION,
}

SYSTEM_MANAGED_FIELDS: Set[str] = {
    "status",
    "validation_status",
    "submitted_by_user_id",
    "assigned_department",
    "created_at",
    "submitted_at",
    "validated_at",
    "rejected_at",
    "reference_code",
}


class ChallengeLocation(BaseModel):
    """Structured location metadata representation."""
    district: str = Field(..., description="Official Jharkhand district name")
    block: Optional[str] = Field(None, max_length=100, description="Administrative block/tehsil")
    village_or_ward: Optional[str] = Field(None, max_length=100, description="Village, ward, or gram panchayat")
    panchayat: Optional[str] = Field(None, max_length=100, description="Panchayat alias for village_or_ward")
    location_description: Optional[str] = Field(None, max_length=500, description="Landmarks or detailed directions")

    model_config = ConfigDict(from_attributes=True)


class ChallengeCreateRequest(BaseModel):
    """
    Client intake payload for submitting a new societal challenge.
    Rejects client attempts to modify workflow, verification, or audit fields.
    """
    title: str = Field(..., min_length=5, max_length=255, description="Clear concise title of the challenge")
    title_hi: Optional[str] = Field(None, max_length=255, description="Hindi title (optional)")
    description: str = Field(..., min_length=10, description="Comprehensive problem statement and community context")
    problem_statement: Optional[str] = Field(None, description="Detailed problem statement breakdown")
    proposed_context: Optional[str] = Field(None, description="Background or local environment context")

    # Location fields (supports flat fields or nested location object)
    district: Optional[str] = Field(None, description="Primary administrative district in Jharkhand")
    block: Optional[str] = Field(None, max_length=100, description="Administrative block")
    village_or_ward: Optional[str] = Field(None, max_length=100, description="Village, ward, or gram panchayat")
    panchayat: Optional[str] = Field(None, max_length=100, description="Panchayat alias")
    location_description: Optional[str] = Field(None, max_length=500, description="Landmarks or description")
    location: Optional[Dict[str, Any]] = Field(None, description="Nested location object from frontend")

    # Classification & Urgency
    domain: Union[SocietalDomain, str] = Field(..., description="Societal domain category")
    subdomain: Optional[str] = Field(None, max_length=100, description="Specialized sub-sector")
    priority: Optional[PriorityLevel] = Field(default=PriorityLevel.MEDIUM, description="Initial priority assessment")
    urgency: Optional[UrgencyLevel] = Field(default=UrgencyLevel.MEDIUM, description="Citizen-reported urgency")

    # Optional Demographics & Context
    affected_population: Optional[str] = Field(None, max_length=255, description="Estimated community demographic affected")
    estimated_beneficiaries: Optional[int] = Field(None, ge=0, description="Estimated number of people impacted")
    existing_attempts: Optional[str] = Field(None, description="Past local interventions or community attempts")
    expected_outcome: Optional[str] = Field(None, description="Desired societal outcome or solution target")
    constraints: Optional[str] = Field(None, description="Known logistical, financial, or geographic bottlenecks")

    # Submitter Context (organization submission is optional)
    submitted_by_organization_id: Optional[str] = Field(None, max_length=36, description="Optional submitting organization")

    # Frontend compatibility placeholders (handled by backend or attachments module)
    attachments: Optional[List[Any]] = Field(default_factory=list, description="Attachment metadata references")
    submittedAt: Optional[str] = Field(None, description="Client advisory submission timestamp")

    @model_validator(mode="before")
    @classmethod
    def validate_and_preprocess(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # 1. Enforce rejection of system-managed fields
        for field_name in SYSTEM_MANAGED_FIELDS:
            if field_name in data and data[field_name] is not None:
                raise ValueError(
                    f"Field '{field_name}' is system-managed and cannot be controlled by client."
                )

        # 2. Extract nested location dictionary if provided
        loc = data.get("location")
        if isinstance(loc, dict):
            if not data.get("district") and loc.get("district"):
                data["district"] = loc["district"]
            if not data.get("block") and loc.get("block"):
                data["block"] = loc["block"]
            p_val = loc.get("panchayat") or loc.get("village_or_ward")
            if not data.get("village_or_ward") and p_val:
                data["village_or_ward"] = p_val
            if not data.get("location_description") and loc.get("location_description"):
                data["location_description"] = loc["location_description"]

        # 3. Map frontend camelCase aliases
        if not data.get("title_hi") and data.get("titleHi"):
            data["title_hi"] = data["titleHi"]
        if not data.get("affected_population") and data.get("affectedPopulation"):
            data["affected_population"] = str(data["affectedPopulation"])

        return data

    @field_validator("title", "description", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: Any, info) -> Any:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError(f"{info.field_name.capitalize()} cannot be empty or whitespace.")
            return cleaned
        return v

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: Optional[str]) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError(
                "District is required. Must be one of the 24 official Jharkhand districts."
            )
        cleaned = v.strip()
        if not is_valid_district(cleaned):
            raise ValueError(
                f"District '{cleaned}' is not a recognized Jharkhand district. "
                f"Must be one of the 24 official districts: {', '.join(JHARKHAND_DISTRICTS)}"
            )
        canonical = get_canonical_district(cleaned)
        if not canonical:
            raise ValueError(f"District '{cleaned}' could not be resolved to a valid district.")
        return canonical

    @field_validator("domain", mode="before")
    @classmethod
    def validate_domain(cls, v: Any) -> SocietalDomain:
        if isinstance(v, SocietalDomain):
            return v
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Domain is required.")

        raw_str = v.strip().lower()
        if raw_str in DOMAIN_ALIASES:
            return DOMAIN_ALIASES[raw_str]

        normalized = normalize_enum_value(SocietalDomain, raw_str)
        if not normalized:
            raise ValueError(
                f"Domain '{v}' is not recognized. Must be a valid societal domain."
            )
        return normalized

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, v: Any) -> Optional[PriorityLevel]:
        if v is None:
            return PriorityLevel.MEDIUM
        if isinstance(v, PriorityLevel):
            return v
        normalized = normalize_enum_value(PriorityLevel, v)
        if not normalized:
            raise ValueError(f"Invalid priority '{v}'. Must be one of: low, medium, high, critical.")
        return normalized

    @field_validator("urgency", mode="before")
    @classmethod
    def validate_urgency(cls, v: Any) -> Optional[UrgencyLevel]:
        if v is None:
            return UrgencyLevel.MEDIUM
        if isinstance(v, UrgencyLevel):
            return v
        normalized = normalize_enum_value(UrgencyLevel, v)
        if not normalized:
            raise ValueError(f"Invalid urgency '{v}'. Must be one of: low, medium, high, critical.")
        return normalized


class ChallengeUpdateRequest(BaseModel):
    """
    Payload for updating an existing societal challenge before workflow lock.
    All fields are optional; prevents arbitrary modifications of system fields.
    """
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    title_hi: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    problem_statement: Optional[str] = Field(None)
    proposed_context: Optional[str] = Field(None)

    district: Optional[str] = Field(None)
    block: Optional[str] = Field(None, max_length=100)
    village_or_ward: Optional[str] = Field(None, max_length=100)
    location_description: Optional[str] = Field(None, max_length=500)
    location: Optional[Dict[str, Any]] = Field(None)

    domain: Optional[Union[SocietalDomain, str]] = None
    subdomain: Optional[str] = Field(None, max_length=100)
    priority: Optional[PriorityLevel] = None
    urgency: Optional[UrgencyLevel] = None

    affected_population: Optional[str] = Field(None, max_length=255)
    estimated_beneficiaries: Optional[int] = Field(None, ge=0)
    existing_attempts: Optional[str] = Field(None)
    expected_outcome: Optional[str] = Field(None)
    constraints: Optional[str] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def validate_update_restrictions(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Enforce rejection of system-managed fields
        for field_name in SYSTEM_MANAGED_FIELDS:
            if field_name in data and data[field_name] is not None:
                raise ValueError(
                    f"Field '{field_name}' is system-managed and cannot be updated directly."
                )

        loc = data.get("location")
        if isinstance(loc, dict):
            if not data.get("district") and loc.get("district"):
                data["district"] = loc["district"]
            if not data.get("block") and loc.get("block"):
                data["block"] = loc["block"]
            p_val = loc.get("panchayat") or loc.get("village_or_ward")
            if not data.get("village_or_ward") and p_val:
                data["village_or_ward"] = p_val
            if not data.get("location_description") and loc.get("location_description"):
                data["location_description"] = loc["location_description"]

        return data

    @field_validator("title", "description", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: Any, info) -> Any:
        if v is not None and isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError(f"{info.field_name.capitalize()} cannot be empty or whitespace.")
            return cleaned
        return v

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("District cannot be empty.")
        if not is_valid_district(cleaned):
            raise ValueError(
                f"District '{cleaned}' is not a recognized Jharkhand district."
            )
        return get_canonical_district(cleaned)

    @field_validator("domain", mode="before")
    @classmethod
    def validate_domain(cls, v: Any) -> Optional[SocietalDomain]:
        if v is None:
            return None
        if isinstance(v, SocietalDomain):
            return v
        raw_str = str(v).strip().lower()
        if raw_str in DOMAIN_ALIASES:
            return DOMAIN_ALIASES[raw_str]
        normalized = normalize_enum_value(SocietalDomain, raw_str)
        if not normalized:
            raise ValueError(f"Domain '{v}' is not recognized.")
        return normalized

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, v: Any) -> Optional[PriorityLevel]:
        if v is None:
            return None
        if isinstance(v, PriorityLevel):
            return v
        normalized = normalize_enum_value(PriorityLevel, v)
        if not normalized:
            raise ValueError(f"Invalid priority '{v}'.")
        return normalized

    @field_validator("urgency", mode="before")
    @classmethod
    def validate_urgency(cls, v: Any) -> Optional[UrgencyLevel]:
        if v is None:
            return None
        if isinstance(v, UrgencyLevel):
            return v
        normalized = normalize_enum_value(UrgencyLevel, v)
        if not normalized:
            raise ValueError(f"Invalid urgency '{v}'.")
        return normalized


class ChallengeResponse(BaseModel):
    """
    Public representation of a societal challenge.
    Converts safely from SQLAlchemy ORM entity.
    """
    id: str
    reference_code: str
    title: str
    title_hi: Optional[str] = None
    description: str
    problem_statement: Optional[str] = None
    proposed_context: Optional[str] = None

    # Location representation (flattened and structured)
    district: str
    block: Optional[str] = None
    village_or_ward: Optional[str] = None
    location_description: Optional[str] = None
    location: ChallengeLocation

    # Classification & Urgency
    domain: SocietalDomain
    subdomain: Optional[str] = None
    priority: PriorityLevel
    urgency: UrgencyLevel

    # Workflow Status
    status: ChallengeStatus
    validation_status: ValidationStatus
    assigned_department: Optional[str] = None

    # Impact & Demographics
    affected_population: Optional[str] = None
    estimated_beneficiaries: Optional[int] = None
    existing_attempts: Optional[str] = None
    expected_outcome: Optional[str] = None
    constraints: Optional[str] = None

    # Submitter Attribution
    submitted_by_user_id: str
    submitted_by_organization_id: Optional[str] = None
    submitted_by: Optional[str] = None

    # Lifecycle Timestamps
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def build_location_and_submitter(cls, data: Any) -> Any:
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            district = getattr(data, "district", "")
            block = getattr(data, "block", None)
            v_or_w = getattr(data, "village_or_ward", None)
            loc_desc = getattr(data, "location_description", None)
            location_dict = {
                "district": district,
                "block": block,
                "village_or_ward": v_or_w,
                "panchayat": v_or_w,
                "location_description": loc_desc,
            }

            user_obj = getattr(data, "submitted_by_user", None)
            submitted_by_name = getattr(user_obj, "full_name", None) if user_obj else None

            return {
                "id": getattr(data, "id", None),
                "reference_code": getattr(data, "reference_code", None),
                "title": getattr(data, "title", None),
                "title_hi": getattr(data, "title_hi", None),
                "description": getattr(data, "description", None),
                "problem_statement": getattr(data, "problem_statement", None),
                "proposed_context": getattr(data, "proposed_context", None),
                "district": district,
                "block": block,
                "village_or_ward": v_or_w,
                "location_description": loc_desc,
                "location": location_dict,
                "domain": getattr(data, "domain", None),
                "subdomain": getattr(data, "subdomain", None),
                "priority": getattr(data, "priority", None),
                "urgency": getattr(data, "urgency", None),
                "status": getattr(data, "status", None),
                "validation_status": getattr(data, "validation_status", None),
                "assigned_department": getattr(data, "assigned_department", None),
                "affected_population": getattr(data, "affected_population", None),
                "estimated_beneficiaries": getattr(data, "estimated_beneficiaries", None),
                "existing_attempts": getattr(data, "existing_attempts", None),
                "expected_outcome": getattr(data, "expected_outcome", None),
                "constraints": getattr(data, "constraints", None),
                "submitted_by_user_id": getattr(data, "submitted_by_user_id", None),
                "submitted_by_organization_id": getattr(data, "submitted_by_organization_id", None),
                "submitted_by": submitted_by_name,
                "submitted_at": getattr(data, "submitted_at", None),
                "created_at": getattr(data, "created_at", None),
                "updated_at": getattr(data, "updated_at", None),
            }

        # If data is a dict and location is missing or partial, populate it
        if isinstance(data, dict) and not data.get("location"):
            data["location"] = {
                "district": data.get("district", ""),
                "block": data.get("block"),
                "village_or_ward": data.get("village_or_ward"),
                "panchayat": data.get("village_or_ward"),
                "location_description": data.get("location_description"),
            }
        return data


class ChallengeListItemResponse(BaseModel):
    """Compact summary response for challenge listings, search, and dashboard grids."""
    id: str
    reference_code: str
    title: str
    description: str
    district: str
    location: Optional[ChallengeLocation] = None
    domain: SocietalDomain
    priority: PriorityLevel
    urgency: UrgencyLevel
    status: ChallengeStatus
    validation_status: ValidationStatus
    submitted_by: Optional[str] = None
    submitted_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def populate_summary_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            district = getattr(data, "district", "")
            block = getattr(data, "block", None)
            v_or_w = getattr(data, "village_or_ward", None)
            user_obj = getattr(data, "submitted_by_user", None)
            submitted_by_name = getattr(user_obj, "full_name", None) if user_obj else None

            return {
                "id": getattr(data, "id", None),
                "reference_code": getattr(data, "reference_code", None),
                "title": getattr(data, "title", None),
                "description": getattr(data, "description", None),
                "district": district,
                "location": {
                    "district": district,
                    "block": block,
                    "village_or_ward": v_or_w,
                    "panchayat": v_or_w,
                },
                "domain": getattr(data, "domain", None),
                "priority": getattr(data, "priority", None),
                "urgency": getattr(data, "urgency", None),
                "status": getattr(data, "status", None),
                "validation_status": getattr(data, "validation_status", None),
                "submitted_by": submitted_by_name,
                "submitted_at": getattr(data, "submitted_at", None),
                "created_at": getattr(data, "created_at", None),
            }
        return data


class ChallengeDetailResponse(ChallengeResponse):
    """Comprehensive detail representation with extended governance tracking."""
    validated_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    duplicate_of_challenge_id: Optional[str] = None


class ChallengeStatusResponse(BaseModel):
    """Lightweight response for status inspection and workflow verification."""
    id: str
    reference_code: str
    status: ChallengeStatus
    validation_status: ValidationStatus
    assigned_department: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
