"""
Phase 1.6 — Challenge Models & Schemas Test Suite.
Verifies the SQLAlchemy 2.0 Challenge model, foreign key integrity, reference codes,
Pydantic v2 validation schemas, ORM serialization, and Alembic migration correctness.
"""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.challenge import Challenge, generate_challenge_reference_code
from app.models.organization import Organization
from app.models.user import User
from app.repositories.challenge_repository import challenge_repository
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeDetailResponse,
    ChallengeListItemResponse,
    ChallengeResponse,
    ChallengeStatusResponse,
    ChallengeUpdateRequest,
)
from app.utils.constants import JHARKHAND_DISTRICTS
from app.utils.enums import (
    ChallengeStatus,
    OrganizationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


# ============================================================================
# 1. Model Structure & Attribute Verification Tests
# ============================================================================

def test_challenge_model_imports_and_structure():
    """1. Challenge model imports correctly and registers on Base.metadata."""
    assert hasattr(Challenge, "__tablename__")
    assert Challenge.__tablename__ == "challenges"
    assert "challenges" in Base.metadata.tables


def test_challenge_model_required_fields_exist():
    """2. All required fields and columns exist on the Challenge model."""
    inspector = inspect(Challenge)
    columns = {col.key for col in inspector.columns}

    required_columns = {
        "id",
        "reference_code",
        "submitted_by_user_id",
        "submitted_by_organization_id",
        "title",
        "title_hi",
        "description",
        "problem_statement",
        "proposed_context",
        "district",
        "block",
        "village_or_ward",
        "location_description",
        "domain",
        "subdomain",
        "priority",
        "urgency",
        "status",
        "validation_status",
        "assigned_department",
        "affected_population",
        "estimated_beneficiaries",
        "existing_attempts",
        "expected_outcome",
        "constraints",
        "submitted_at",
        "created_at",
        "updated_at",
        "validated_at",
        "rejected_at",
        "duplicate_of_challenge_id",
    }
    missing = required_columns - columns
    assert not missing, f"Missing columns in Challenge model: {missing}"


def test_challenge_default_status_is_submitted(db_session):
    """3. Default status is ChallengeStatus.SUBMITTED."""
    user = User(
        full_name="Citizen Tester",
        email="citizen.tester@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
    )
    db_session.add(user)
    db_session.commit()

    challenge = Challenge(
        submitted_by_user_id=user.id,
        title="Contaminated Well in Village",
        description="The main tube well has heavy iron and arsenic levels affecting 200 families.",
        district="Ranchi",
        domain=SocietalDomain.WATER,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    assert challenge.status == ChallengeStatus.SUBMITTED
    assert challenge.status.value == "submitted"


def test_challenge_default_validation_status_is_pending(db_session):
    """4. Default validation status is ValidationStatus.PENDING."""
    user = User(
        full_name="Nodal Reviewee",
        email="nodal.reviewee@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
    )
    db_session.add(user)
    db_session.commit()

    challenge = Challenge(
        submitted_by_user_id=user.id,
        title="Primary School Roof Leak",
        description="Monsoon rainwater leaks into classrooms preventing 80 children from studying.",
        district="Dumka",
        domain=SocietalDomain.EDUCATION,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    assert challenge.validation_status == ValidationStatus.PENDING
    assert challenge.validation_status.value == "pending"


def test_foreign_keys_configured_correctly(db_session):
    """5. Foreign keys link cleanly to User and Organization without circular import or cascade errors."""
    user = User(
        full_name="NGO Submitter",
        email="ngo.submitter@example.com",
        password_hash="hashedpass",
        role=UserRole.COMMUNITY_ORGANIZATION,
    )
    org = Organization(
        name="Chotanagpur Green Foundation",
        organization_type=OrganizationType.NGO,
        district="Ranchi",
    )
    db_session.add_all([user, org])
    db_session.commit()

    challenge = Challenge(
        submitted_by_user_id=user.id,
        submitted_by_organization_id=org.id,
        title="Solar Micro-Grid for Forest Hamlet",
        description="A remote tribal settlement lacks electricity for cold storage and lighting.",
        district="Khunti",
        domain=SocietalDomain.ENERGY,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    assert challenge.submitted_by_user.id == user.id
    assert challenge.submitted_by_organization.id == org.id
    assert challenge in user.challenges
    assert challenge in org.challenges


def test_reference_code_generation_and_uniqueness(db_session):
    """6. Reference codes follow JS-YYYY-XXXXXX format and prevent duplicates."""
    ref1 = generate_challenge_reference_code()
    ref2 = generate_challenge_reference_code()
    assert ref1.startswith(f"JS-{datetime.now(timezone.utc).year}-")
    assert len(ref1) == 14  # JS-YYYY-XXXXXX (2 + 1 + 4 + 1 + 6 = 14)
    assert ref1 != ref2

    user = User(
        full_name="Duplicate Ref Submitter",
        email="dup.ref@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
    )
    db_session.add(user)
    db_session.commit()

    c1 = Challenge(
        reference_code="JS-2026-UNIQUE1",
        submitted_by_user_id=user.id,
        title="Clean Water Project",
        description="Description for clean water project in rural district.",
        district="Gumla",
        domain=SocietalDomain.WATER,
    )
    db_session.add(c1)
    db_session.commit()

    # Attempting to save a duplicate reference code must trigger an IntegrityError
    c2 = Challenge(
        reference_code="JS-2026-UNIQUE1",
        submitted_by_user_id=user.id,
        title="Another Project",
        description="Duplicate reference code test description.",
        district="Gumla",
        domain=SocietalDomain.WATER,
    )
    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ============================================================================
# 2. Pydantic v2 Schema Validation Tests
# ============================================================================

def test_valid_challenge_payload_passes():
    """7. Valid challenge intake payload validates successfully."""
    payload = {
        "title": "Irrigation canal desiltation in Kanke block",
        "description": "The primary distribution canal is clogged with silt, cutting water supply to 500 acres of paddy fields.",
        "district": "Ranchi",
        "block": "Kanke",
        "domain": "agriculture",
        "priority": "high",
        "urgency": "critical",
        "affected_population": "500 farming families",
        "estimated_beneficiaries": 2500,
    }
    schema = ChallengeCreateRequest(**payload)
    assert schema.title == payload["title"]
    assert schema.district == "Ranchi"
    assert schema.domain == SocietalDomain.AGRICULTURE
    assert schema.priority == PriorityLevel.HIGH
    assert schema.urgency == UrgencyLevel.CRITICAL


def test_missing_title_fails():
    """8. Missing title fails Pydantic validation."""
    payload = {
        "description": "A valid description describing the problem statement in detail.",
        "district": "Ranchi",
        "domain": "agriculture",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "title" in str(exc.value)


def test_missing_description_fails():
    """9. Missing description fails Pydantic validation."""
    payload = {
        "title": "A Valid Problem Title",
        "district": "Ranchi",
        "domain": "agriculture",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "description" in str(exc.value)


def test_invalid_district_fails():
    """10. District outside the 24 official Jharkhand districts fails validation."""
    payload = {
        "title": "District Validation Check",
        "description": "Testing that out-of-state or non-existent districts are rejected.",
        "district": "Patna",  # Bihar, not Jharkhand
        "domain": "healthcare",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "not a recognized Jharkhand district" in str(exc.value)


def test_invalid_domain_fails():
    """11. Non-existent domain fails validation."""
    payload = {
        "title": "Domain Validation Check",
        "description": "Testing that invalid domain identifiers are rejected cleanly.",
        "district": "Hazaribagh",
        "domain": "cryptocurrency_trading",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "Domain" in str(exc.value)


def test_invalid_priority_fails():
    """12. Invalid priority string fails validation."""
    payload = {
        "title": "Priority Validation Check",
        "description": "Testing that invalid priority identifiers fail validation.",
        "district": "Bokaro",
        "domain": "infrastructure",
        "priority": "super_urgent_emergency",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "priority" in str(exc.value).lower()


def test_invalid_urgency_fails():
    """13. Invalid urgency string fails validation."""
    payload = {
        "title": "Urgency Validation Check",
        "description": "Testing that invalid urgency identifiers fail validation.",
        "district": "Bokaro",
        "domain": "infrastructure",
        "urgency": "yesterday",
    }
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(**payload)
    assert "urgency" in str(exc.value).lower()


def test_empty_strings_fail():
    """14. Whitespace-only strings fail validation for required fields."""
    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(
            title="   ",
            description="Valid description here for testing.",
            district="Ranchi",
            domain="education",
        )
    assert "Title cannot be empty" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        ChallengeCreateRequest(
            title="Valid Problem Title",
            description="          ",
            district="Ranchi",
            domain="education",
        )
    assert "Description cannot be empty" in str(exc.value)


def test_system_managed_fields_cannot_be_client_controlled():
    """15. System-managed fields cannot be set or overridden by the client."""
    forbidden_inputs = [
        {"status": "validated"},
        {"validation_status": "validated"},
        {"submitted_by_user_id": "fake-user-id"},
        {"created_at": "2026-01-01T00:00:00Z"},
        {"submitted_at": "2026-01-01T00:00:00Z"},
        {"validated_at": "2026-01-01T00:00:00Z"},
        {"assigned_department": "Dept of Rural Development"},
        {"reference_code": "JS-HACK-12345"},
    ]
    base_payload = {
        "title": "System Field Protection Test",
        "description": "Ensuring clients cannot tamper with governance lifecycle fields.",
        "district": "Dhanbad",
        "domain": "environment",
    }

    for forbidden in forbidden_inputs:
        tampered = {**base_payload, **forbidden}
        with pytest.raises(ValidationError) as exc:
            ChallengeCreateRequest(**tampered)
        field_tested = list(forbidden.keys())[0]
        assert f"Field '{field_tested}' is system-managed" in str(exc.value)


def test_partial_update_schema_works():
    """16. ChallengeUpdateRequest permits partial updates while forbidding system fields."""
    # 1. Valid partial update
    update_data = {
        "title": "Updated Title for Clean Drinking Water",
        "urgency": "critical",
    }
    update_schema = ChallengeUpdateRequest(**update_data)
    assert update_schema.title == "Updated Title for Clean Drinking Water"
    assert update_schema.urgency == UrgencyLevel.CRITICAL
    assert update_schema.description is None
    assert update_schema.district is None

    # 2. Empty update passes
    empty_update = ChallengeUpdateRequest()
    assert empty_update.title is None

    # 3. System fields are rejected in update
    with pytest.raises(ValidationError) as exc:
        ChallengeUpdateRequest(status="validated")
    assert "system-managed" in str(exc.value)


def test_orm_response_serialization_works(db_session):
    """17. Challenge ORM model serializes properly into Pydantic v2 response schemas."""
    user = User(
        full_name="Deepa Soren",
        email="deepa.soren@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
    )
    db_session.add(user)
    db_session.commit()

    challenge = Challenge(
        submitted_by_user_id=user.id,
        title="Lack of Cold Storage for Local Tomato Harvest",
        description="Local farmers in Ormanjhi suffer 40% post-harvest loss every summer due to lack of cold storage.",
        district="Ranchi",
        block="Ormanjhi",
        village_or_ward="Irba",
        domain=SocietalDomain.AGRICULTURE,
        priority=PriorityLevel.HIGH,
        urgency=UrgencyLevel.HIGH,
        affected_population="300 farmers",
        estimated_beneficiaries=1200,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)

    # 1. ChallengeResponse serialization
    resp = ChallengeResponse.model_validate(challenge)
    assert resp.id == challenge.id
    assert resp.reference_code == challenge.reference_code
    assert resp.title == challenge.title
    assert resp.district == "Ranchi"
    assert resp.location.district == "Ranchi"
    assert resp.location.block == "Ormanjhi"
    assert resp.location.panchayat == "Irba"
    assert resp.submitted_by == "Deepa Soren"
    assert resp.domain == SocietalDomain.AGRICULTURE
    assert resp.status == ChallengeStatus.SUBMITTED
    assert resp.validation_status == ValidationStatus.PENDING

    # 2. ChallengeListItemResponse serialization
    list_item = ChallengeListItemResponse.model_validate(challenge)
    assert list_item.id == challenge.id
    assert list_item.title == challenge.title
    assert list_item.submitted_by == "Deepa Soren"

    # 3. ChallengeDetailResponse serialization
    detail = ChallengeDetailResponse.model_validate(challenge)
    assert detail.id == challenge.id
    assert detail.duplicate_of_challenge_id is None

    # 4. ChallengeStatusResponse serialization
    status_resp = ChallengeStatusResponse.model_validate(challenge)
    assert status_resp.id == challenge.id
    assert status_resp.status == ChallengeStatus.SUBMITTED
    assert status_resp.validation_status == ValidationStatus.PENDING


# ============================================================================
# 3. Frontend Compatibility & Domain Alias Tests
# ============================================================================

def test_frontend_nested_location_support():
    """Support nested location object as submitted by 2_CitizenPortal.jsx."""
    payload = {
        "title": "Solar Powered Pumping in Bishunpur",
        "description": "Replacing diesel pumps with solar pumps for community irrigation.",
        "location": {
            "district": "Gumla",
            "block": "Bishunpur",
            "panchayat": "Kisko Ward 3",
        },
        "domain": "clean_energy",  # Frontend domain alias
        "urgency": "HIGH",         # Frontend uppercase urgency
        "attachments": [],
    }
    schema = ChallengeCreateRequest(**payload)
    assert schema.district == "Gumla"
    assert schema.block == "Bishunpur"
    assert schema.village_or_ward == "Kisko Ward 3"
    assert schema.domain == SocietalDomain.ENERGY
    assert schema.urgency == UrgencyLevel.HIGH


def test_frontend_domain_aliases_resolution():
    """Resolve frontend domain aliases to canonical SocietalDomain enum."""
    aliases = {
        "water_sanitation": SocietalDomain.WATER,
        "clean_energy": SocietalDomain.ENERGY,
        "smart_education": SocietalDomain.EDUCATION,
        "waste_management": SocietalDomain.SANITATION,
    }
    for alias, expected in aliases.items():
        req = ChallengeCreateRequest(
            title="Domain Alias Test Title",
            description="Testing automated normalization of frontend domain options.",
            district="Ranchi",
            domain=alias,
        )
        assert req.domain == expected


# ============================================================================
# 4. Repository & Database Isolation Tests
# ============================================================================

def test_challenge_repository_helpers(db_session):
    """Verify ChallengeRepository create, get_by_id, and get_by_reference_code."""
    user = User(
        full_name="Repo Submitter",
        email="repo.submitter@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
    )
    db_session.add(user)
    db_session.commit()

    challenge = Challenge(
        submitted_by_user_id=user.id,
        title="Check Dam Maintenance on Subarnarekha Tributary",
        description="Check dam gates are rusted and leaking stored water before the dry season.",
        district="East Singhbhum",
        domain=SocietalDomain.WATER,
    )
    created = challenge_repository.create(db_session, challenge)
    assert created.id is not None
    assert created.reference_code.startswith("JS-")

    found_by_id = challenge_repository.get_by_id(db_session, created.id)
    assert found_by_id is not None
    assert found_by_id.title == created.title

    found_by_ref = challenge_repository.get_by_reference_code(db_session, created.reference_code)
    assert found_by_ref is not None
    assert found_by_ref.id == created.id

    assert challenge_repository.get_by_id(db_session, "non-existent-uuid") is None
    assert challenge_repository.get_by_reference_code(db_session, "JS-9999-NOTFOUND") is None


def test_challenge_alembic_migration_creates_table_and_indexes(tmp_path, monkeypatch):
    """18, 19, 20. Verify Alembic migration 0004 applies, creates challenges table with indexes, and no unrelated tables."""
    import os
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect
    from app.core.config import settings

    db_path = tmp_path / "migration_test.db"
    db_url = f"sqlite:///{db_path}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setattr(settings, "DATABASE_URL", db_url)

    ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
    cfg = Config(ini_path)
    cfg.set_main_option("sqlalchemy.url", db_url)

    # Upgrade to head
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        # Verify expected tables
        assert "challenges" in tables
        assert "users" in tables
        assert "organizations" in tables
        assert "organization_memberships" in tables
        assert "attachments" in tables
        assert "government_reviews" in tables
        assert "notifications" in tables
        assert "audit_logs" in tables
        assert "alembic_version" in tables

        # Verify NO Phase 2.11+ or Phase 3 tables exist
        prohibited_tables = {"universities", "impact_verifications", "partnerships", "field_trials", "solutions"}
        assert not (prohibited_tables & tables), f"Prohibited tables found: {prohibited_tables & tables}"

        # Verify columns and indexes on challenges table
        cols = {col["name"] for col in inspector.get_columns("challenges")}
        assert "reference_code" in cols
        assert "status" in cols
        assert "validation_status" in cols
        assert "district" in cols
        assert "domain" in cols
        assert "submitted_by_user_id" in cols

        indexes = {idx["name"] for idx in inspector.get_indexes("challenges")}
        assert any("reference_code" in name for name in indexes)
        assert any("status" in name for name in indexes)
        assert any("district" in name for name in indexes)
        assert any("domain" in name for name in indexes)
    finally:
        engine.dispose()

