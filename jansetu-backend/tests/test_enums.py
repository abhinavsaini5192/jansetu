import pytest
from pydantic import BaseModel, ValidationError

from app.utils.constants import (
    DOMAIN_METADATA,
    JHARKHAND_DISTRICTS,
    get_canonical_district,
    get_canonical_domain,
    is_valid_district,
    is_valid_domain,
)
from app.utils.enums import (
    AuditAction,
    ChallengeStatus,
    NotificationType,
    OrganizationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
    enum_values,
    normalize_enum_value,
)


def test_user_roles_members_and_values():
    """1. Verify UserRole enum contains exact members with stable string values."""
    expected = {
        "CITIZEN": "citizen",
        "COMMUNITY_ORGANIZATION": "community_organization",
        "GOVERNMENT_ADMIN": "government_admin",
        "DISTRICT_NODAL_OFFICER": "district_nodal_officer",
        "UNIVERSITY_ADMIN": "university_admin",
        "FACULTY": "faculty",
        "STUDENT": "student",
        "RESEARCHER": "researcher",
        "INDUSTRY_PARTNER": "industry_partner",
        "CSR_PARTNER": "csr_partner",
        "PLATFORM_ADMIN": "platform_admin",
    }
    assert len(UserRole) == len(expected)
    for name, value in expected.items():
        assert getattr(UserRole, name).value == value


def test_organization_types_members_and_values():
    """2. Verify OrganizationType contains exact members with stable string values."""
    expected = {
        "GOVERNMENT": "government",
        "UNIVERSITY": "university",
        "INDUSTRY": "industry",
        "NGO": "ngo",
        "COMMUNITY": "community",
        "RESEARCH_LAB": "research_lab",
        "STARTUP": "startup",
    }
    assert len(OrganizationType) == len(expected)
    for name, value in expected.items():
        assert getattr(OrganizationType, name).value == value


def test_challenge_and_validation_statuses():
    """3. Verify ChallengeStatus and ValidationStatus lifecycle members."""
    expected_challenge_statuses = {
        "SUBMITTED": "submitted",
        "UNDER_REVIEW": "under_review",
        "VALIDATED": "validated",
        "REJECTED": "rejected",
        "DUPLICATE": "duplicate",
        "NEEDS_CLARIFICATION": "needs_clarification",
        "ASSIGNED": "assigned",
    }
    assert len(ChallengeStatus) == len(expected_challenge_statuses)
    for name, value in expected_challenge_statuses.items():
        assert getattr(ChallengeStatus, name).value == value

    expected_validation_statuses = {
        "PENDING": "pending",
        "VALIDATED": "validated",
        "REJECTED": "rejected",
        "DUPLICATE": "duplicate",
        "NEEDS_CLARIFICATION": "needs_clarification",
    }
    assert len(ValidationStatus) == len(expected_validation_statuses)
    for name, value in expected_validation_statuses.items():
        assert getattr(ValidationStatus, name).value == value


def test_priority_and_urgency_levels():
    """4. Verify PriorityLevel and UrgencyLevel are distinct enums with identical levels."""
    levels = {"LOW": "low", "MEDIUM": "medium", "HIGH": "high", "CRITICAL": "critical"}

    assert PriorityLevel is not UrgencyLevel
    assert len(PriorityLevel) == len(levels)
    assert len(UrgencyLevel) == len(levels)

    for name, value in levels.items():
        assert getattr(PriorityLevel, name).value == value
        assert getattr(UrgencyLevel, name).value == value


def test_notification_types_and_audit_actions():
    """5. Verify NotificationType and AuditAction members and values."""
    expected_notifications = {
        "CHALLENGE_SUBMITTED": "challenge_submitted",
        "CHALLENGE_VALIDATED": "challenge_validated",
        "CHALLENGE_REJECTED": "challenge_rejected",
        "CHALLENGE_MARKED_DUPLICATE": "challenge_marked_duplicate",
        "CLARIFICATION_REQUESTED": "clarification_requested",
        "DEPARTMENT_ASSIGNED": "department_assigned",
        "SYSTEM": "system",
        "SECURITY": "security",
        "GENERAL": "general",
    }
    assert len(NotificationType) == len(expected_notifications)
    for name, value in expected_notifications.items():
        assert getattr(NotificationType, name).value == value

    expected_audit_actions = {
        "CREATE", "READ", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "REGISTER",
        "SUBMIT", "VALIDATE", "REJECT", "MARK_DUPLICATE", "REQUEST_CLARIFICATION",
        "ASSIGN_DEPARTMENT", "UPLOAD", "DOWNLOAD", "STATUS_CHANGE"
    }
    assert {m.name for m in AuditAction} == expected_audit_actions
    for member in AuditAction:
        assert member.value == member.name.lower()


def test_jharkhand_districts_count_and_uniqueness():
    """6. Verify that JHARKHAND_DISTRICTS contains exactly 24 unique districts."""
    assert isinstance(JHARKHAND_DISTRICTS, tuple)
    assert len(JHARKHAND_DISTRICTS) == 24
    assert len(set(JHARKHAND_DISTRICTS)) == 24
    assert "Ranchi" in JHARKHAND_DISTRICTS
    assert "Gumla" in JHARKHAND_DISTRICTS
    assert "Dhanbad" in JHARKHAND_DISTRICTS


def test_is_valid_district_helper():
    """7. Verify district validation handles case-insensitivity and whitespace."""
    assert is_valid_district("Ranchi") is True
    assert is_valid_district("ranchi") is True
    assert is_valid_district("  GUMLA  ") is True
    assert is_valid_district("East Singhbhum") is True
    assert is_valid_district("east singhbhum") is True

    # Invalid districts
    assert is_valid_district("Patna") is False
    assert is_valid_district("Delhi") is False
    assert is_valid_district("UnknownDistrict") is False
    assert is_valid_district("") is False
    assert is_valid_district(None) is False


def test_get_canonical_district_helper():
    """8. Verify get_canonical_district resolves to the official spelling."""
    assert get_canonical_district("ranchi") == "Ranchi"
    assert get_canonical_district("EAST SINGHBhum") == "East Singhbhum"
    assert get_canonical_district("gumla") == "Gumla"
    assert get_canonical_district("invalid") is None
    assert get_canonical_district(None) is None


def test_societal_domains_and_metadata():
    """9. Verify SocietalDomain values and DOMAIN_METADATA mapping."""
    domains = enum_values(SocietalDomain)
    assert len(domains) >= 20
    assert "education" in domains
    assert "healthcare" in domains
    assert "agriculture" in domains
    assert "water" in domains

    # Verify every domain has English and Hindi labels in metadata
    for domain in SocietalDomain:
        assert domain.value in DOMAIN_METADATA
        meta = DOMAIN_METADATA[domain.value]
        assert "label_en" in meta and len(meta["label_en"]) > 0
        assert "label_hi" in meta and len(meta["label_hi"]) > 0


def test_is_valid_domain_helper():
    """10. Verify domain validation handles canonical and case-insensitive resolution."""
    assert is_valid_domain("education") is True
    assert is_valid_domain("EDUCATION") is True
    assert is_valid_domain("healthcare") is True
    assert is_valid_domain("water") is True

    # Invalid domains
    assert is_valid_domain("cryptocurrency") is False
    assert is_valid_domain("alien_technology") is False
    assert is_valid_domain("") is False
    assert is_valid_domain(None) is False


def test_get_canonical_domain_helper():
    """11. Verify get_canonical_domain returns normalized string."""
    assert get_canonical_domain("EDUCATION") == "education"
    assert get_canonical_domain("healthcare") == "healthcare"
    assert get_canonical_domain("unknown") is None


def test_pydantic_v2_enum_serialization_and_validation():
    """12. Verify that string enums integrate seamlessly with Pydantic v2 models."""
    class SampleIntake(BaseModel):
        role: UserRole
        status: ChallengeStatus
        priority: PriorityLevel
        urgency: UrgencyLevel
        domain: SocietalDomain

    # Valid instantiation from strings
    obj = SampleIntake(
        role="citizen",
        status="submitted",
        priority="high",
        urgency="critical",
        domain="education",
    )
    assert obj.role == UserRole.CITIZEN
    assert obj.status == ChallengeStatus.SUBMITTED
    assert obj.priority == PriorityLevel.HIGH
    assert obj.urgency == UrgencyLevel.CRITICAL
    assert obj.domain == SocietalDomain.EDUCATION

    # JSON serialization yields clean strings
    json_data = obj.model_dump()
    assert json_data["role"] == "citizen"
    assert json_data["status"] == "submitted"
    assert json_data["priority"] == "high"

    # Invalid enum value raises ValidationError
    with pytest.raises(ValidationError):
        SampleIntake(
            role="unauthorized_hacker",
            status="submitted",
            priority="high",
            urgency="critical",
            domain="education",
        )


def test_normalize_enum_value_helper():
    """13. Verify normalize_enum_value helper functionality."""
    assert normalize_enum_value(UserRole, "citizen") == UserRole.CITIZEN
    assert normalize_enum_value(UserRole, "CITIZEN") == UserRole.CITIZEN
    assert normalize_enum_value(UserRole, "Citizen") == UserRole.CITIZEN
    assert normalize_enum_value(UserRole, UserRole.CITIZEN) == UserRole.CITIZEN
    assert normalize_enum_value(UserRole, "invalid_role") is None
    assert normalize_enum_value(UserRole, None) is None
