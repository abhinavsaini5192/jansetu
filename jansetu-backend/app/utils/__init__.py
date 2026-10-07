"""
JanSetu Utilities Package.
Exposes centralized enums, district constants, and validation helpers.
"""
from app.utils.constants import (
    ALLOWED_ATTACHMENT_EXTENSIONS,
    ALLOWED_ATTACHMENT_MIME_TYPES,
    DEFAULT_PAGE_SIZE,
    DOMAIN_METADATA,
    JHARKHAND_DISTRICTS,
    MAX_ATTACHMENT_SIZE_BYTES,
    MAX_PAGE_SIZE,
    SUPPORTED_LANGUAGES,
    get_canonical_district,
    get_canonical_domain,
    is_valid_district,
    is_valid_domain,
)
from app.utils.enums import (
    AuditAction,
    ChallengeStatus,
    NotificationType,
    OrganizationMembershipRole,
    OrganizationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
    enum_values,
    normalize_enum_value,
)

__all__ = [
    "UserRole",
    "OrganizationType",
    "OrganizationMembershipRole",
    "ChallengeStatus",
    "ValidationStatus",
    "PriorityLevel",
    "UrgencyLevel",
    "NotificationType",
    "AuditAction",
    "SocietalDomain",
    "enum_values",
    "normalize_enum_value",
    "JHARKHAND_DISTRICTS",
    "SUPPORTED_LANGUAGES",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "ALLOWED_ATTACHMENT_EXTENSIONS",
    "ALLOWED_ATTACHMENT_MIME_TYPES",
    "MAX_ATTACHMENT_SIZE_BYTES",
    "DOMAIN_METADATA",
    "is_valid_district",
    "get_canonical_district",
    "is_valid_domain",
    "get_canonical_domain",
]
