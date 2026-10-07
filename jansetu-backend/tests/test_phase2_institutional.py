"""
Focused Test Suite for JanSetu Phase 2.1 – 2.5 Institutional Collaboration.
Covers:
- Phase 2.1: University Directory (listing, permissions, verification)
- Phase 2.2: Departments & Capabilities (creation, association, cross-institution isolation)
- Phase 2.3: Deterministic Explainable Matching (rules, rejection of unvalidated challenges)
- Phase 2.4: Challenge Assignment & Acceptance (mandates, acceptance, transitions, RBAC)
- Phase 2.5: Project Workspace (creation, idempotency, authorization, end-to-end integration)
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.models.audit_log import AuditLog
from app.models.capability import Capability
from app.models.challenge import Challenge
from app.models.challenge_assignment import ChallengeAssignment
from app.models.department import Department
from app.models.notification import Notification
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.university_profile import UniversityProfile
from app.models.user import User
from app.utils.enums import (
    AssignmentStatus,
    AuditAction,
    ChallengeStatus,
    InstitutionCategory,
    NotificationType,
    OrganizationMembershipRole,
    OrganizationType,
    PriorityLevel,
    ProjectStatus,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


@pytest.fixture
def platform_admin_user(db_session):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="Platform Super Admin",
        email=f"platform.admin.{uid}@jansetu.gov.in",
        password_hash="securehash",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def platform_admin_headers(platform_admin_user):
    token = create_access_token(
        subject=platform_admin_user.id,
        additional_claims={"email": platform_admin_user.email, "role": platform_admin_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def govt_user(db_session):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="Ranchi Nodal Officer",
        email=f"nodal.ranchi.{uid}@jharkhand.gov.in",
        password_hash="securehash",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def govt_headers(govt_user):
    token = create_access_token(
        subject=govt_user.id,
        additional_claims={"email": govt_user.email, "role": govt_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_user(db_session):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="Citizen Submitter",
        email=f"citizen.{uid}@example.com",
        password_hash="securehash",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_headers(citizen_user):
    token = create_access_token(
        subject=citizen_user.id,
        additional_claims={"email": citizen_user.email, "role": citizen_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_citizen(db_session):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="Unaffiliated Citizen",
        email=f"unaffiliated.{uid}@example.com",
        password_hash="securehash",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_citizen_headers(other_citizen):
    token = create_access_token(
        subject=other_citizen.id,
        additional_claims={"email": other_citizen.email, "role": other_citizen.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def university_a(db_session):
    uid = uuid.uuid4().hex[:8]
    org = Organization(
        name=f"Birsa Institute of Technology Sindri {uid}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Dhanbad",
        state="Jharkhand",
        is_active=True,
        is_verified=True,
    )
    db_session.add(org)
    db_session.flush()

    prof = UniversityProfile(
        organization_id=org.id,
        institution_category=InstitutionCategory.ENGINEERING_COLLEGE,
        accreditation_details="NAAC A+",
        district="Dhanbad",
        is_verified=True,
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def uni_admin_a(db_session, university_a):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="BIT Admin",
        email=f"admin.bit.{uid}@bit.ac.in",
        password_hash="securehash",
        role=UserRole.UNIVERSITY_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    m = OrganizationMembership(
        user_id=user.id,
        organization_id=university_a.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    )
    db_session.add(m)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def uni_admin_a_headers(uni_admin_a):
    token = create_access_token(
        subject=uni_admin_a.id,
        additional_claims={"email": uni_admin_a.email, "role": uni_admin_a.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def university_b(db_session):
    uid = uuid.uuid4().hex[:8]
    org = Organization(
        name=f"Ranchi University {uid}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Ranchi",
        state="Jharkhand",
        is_active=True,
        is_verified=True,
    )
    db_session.add(org)
    db_session.flush()

    prof = UniversityProfile(
        organization_id=org.id,
        institution_category=InstitutionCategory.UNIVERSITY,
        accreditation_details="NAAC A",
        district="Ranchi",
        is_verified=True,
        is_active=True,
    )
    db_session.add(prof)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def uni_admin_b(db_session, university_b):
    uid = uuid.uuid4().hex[:8]
    user = User(
        full_name="RU Admin",
        email=f"admin.ru.{uid}@ranchiuniv.ac.in",
        password_hash="securehash",
        role=UserRole.UNIVERSITY_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    m = OrganizationMembership(
        user_id=user.id,
        organization_id=university_b.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    )
    db_session.add(m)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def uni_admin_b_headers(uni_admin_b):
    token = create_access_token(
        subject=uni_admin_b.id,
        additional_claims={"email": uni_admin_b.email, "role": uni_admin_b.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def validated_challenge(db_session, citizen_user):
    challenge = Challenge(
        submitted_by_user_id=citizen_user.id,
        title="High Arsenic and Fluoride in Groundwater Wells",
        description="Groundwater contamination impacting 5000 villagers in Kanke block.",
        problem_statement="Drinking water exceeds permissible fluoride limits requiring low-cost filtration.",
        district="Ranchi",
        domain=SocietalDomain.WATER,
        priority=PriorityLevel.CRITICAL,
        urgency=UrgencyLevel.CRITICAL,
        status=ChallengeStatus.VALIDATED,
        validation_status=ValidationStatus.VALIDATED,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


# ==============================================================================
# PHASE 2.1: UNIVERSITY DIRECTORY
# ==============================================================================

def test_university_listing_active_and_verified(client: TestClient, db_session, university_a):
    """1. Public listing returns only active and verified university records."""
    uid = uuid.uuid4().hex[:8]
    unverified = Organization(
        name=f"Unverified Tech Academy {uid}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Ranchi",
        is_active=True,
        is_verified=False,
    )
    db_session.add(unverified)
    db_session.commit()

    resp = client.get("/api/v1/universities")
    assert resp.status_code == 200
    data = resp.json()["data"]
    names = [u["name"] for u in data]
    assert university_a.name in names
    assert unverified.name not in names


def test_unauthorized_user_cannot_create_or_verify_university(
    client: TestClient,
    citizen_headers,
    university_a,
):
    """2. Citizens cannot register universities or modify verification status."""
    uid = uuid.uuid4().hex[:8]
    create_resp = client.post(
        "/api/v1/universities",
        headers=citizen_headers,
        json={"name": f"Fake University {uid}", "district": "Ranchi"},
    )
    assert create_resp.status_code == 403

    verify_resp = client.patch(
        f"/api/v1/universities/{university_a.id}/verify",
        headers=citizen_headers,
        json={"is_verified": True},
    )
    assert verify_resp.status_code == 403


# ==============================================================================
# PHASE 2.2: DEPARTMENTS & CAPABILITIES
# ==============================================================================

def test_university_admin_can_create_department(
    client: TestClient,
    uni_admin_a_headers,
    university_a,
):
    """3. University admin can create a department for their university."""
    uid = uuid.uuid4().hex[:8]
    payload = {
        "name": f"Department of Environmental Engineering {uid}",
        "code": "ENV",
        "description": "Specializing in water treatment and hydrology",
        "contact_email": "env@bit.ac.in",
    }
    resp = client.post(
        f"/api/v1/universities/{university_a.id}/departments",
        headers=uni_admin_a_headers,
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == payload["name"]
    assert data["organization_id"] == university_a.id


def test_user_cannot_modify_another_university_department(
    client: TestClient,
    db_session,
    uni_admin_b_headers,
    university_a,
):
    """4. University B admin cannot modify University A's department."""
    uid = uuid.uuid4().hex[:8]
    dept = Department(
        organization_id=university_a.id,
        name=f"Mechanical Engineering {uid}",
        code="MECH",
        is_active=True,
    )
    db_session.add(dept)
    db_session.commit()

    resp = client.patch(
        f"/api/v1/departments/{dept.id}",
        headers=uni_admin_b_headers,
        json={"name": "Hacked Department Name"},
    )
    assert resp.status_code == 403


def test_department_capability_association(
    client: TestClient,
    db_session,
    uni_admin_a_headers,
    university_a,
):
    """5. Linking and unlinking capabilities to a department works properly."""
    uid = uuid.uuid4().hex[:8]
    dept = Department(
        organization_id=university_a.id,
        name=f"Civil Engineering {uid}",
        is_active=True,
    )
    cap = Capability(
        name=f"Water Filtration and Contaminant Detection {uid}",
        domain=SocietalDomain.WATER,
        keywords="fluoride arsenic filtration water groundwater",
        is_active=True,
    )
    db_session.add_all([dept, cap])
    db_session.commit()

    link_resp = client.post(
        f"/api/v1/departments/{dept.id}/capabilities",
        headers=uni_admin_a_headers,
        json={"capability_id": cap.id},
    )
    assert link_resp.status_code == 200
    caps = link_resp.json()["data"]["capabilities"]
    assert any(c["id"] == cap.id for c in caps)

    unlink_resp = client.delete(
        f"/api/v1/departments/{dept.id}/capabilities/{cap.id}",
        headers=uni_admin_a_headers,
    )
    assert unlink_resp.status_code == 200
    caps_after = unlink_resp.json()["data"]["capabilities"]
    assert not any(c["id"] == cap.id for c in caps_after)


# ==============================================================================
# PHASE 2.3: EXPLAINABLE UNIVERSITY MATCHING
# ==============================================================================

def test_validated_challenge_returns_deterministic_matches(
    client: TestClient,
    db_session,
    validated_challenge,
    university_b,
):
    """6. Validated challenge returns deterministic explainable matches."""
    uid = uuid.uuid4().hex[:8]
    dept = Department(
        organization_id=university_b.id,
        name=f"Center for Water Resources {uid}",
        is_active=True,
    )
    cap = Capability(
        name=f"Groundwater Arsenic Testing {uid}",
        domain=SocietalDomain.WATER,
        keywords="arsenic groundwater filtration fluoride",
        is_active=True,
    )
    dept.capabilities.append(cap)
    db_session.add_all([dept, cap])
    db_session.commit()

    resp = client.get(f"/api/v1/challenges/{validated_challenge.id}/matches")
    assert resp.status_code == 200
    data = resp.json()
    assert "matches" in data
    assert len(data["matches"]) > 0

    best = data["matches"][0]
    assert best["overallMatch"] > 50
    assert len(best["match_reasons"]) > 0
    assert "explainableFactors" in best
    assert "domain_alignment" in best["explainableFactors"]
    assert "district_proximity" in best["explainableFactors"]


def test_non_validated_challenge_matching_rejected(
    client: TestClient,
    db_session,
    citizen_user,
):
    """7. Non-validated challenge cannot enter institutional matching."""
    pending_challenge = Challenge(
        submitted_by_user_id=citizen_user.id,
        title="Unreviewed Intake",
        description="Pending review",
        district="Ranchi",
        domain=SocietalDomain.HEALTHCARE,
        status=ChallengeStatus.SUBMITTED,
        validation_status=ValidationStatus.PENDING,
    )
    db_session.add(pending_challenge)
    db_session.commit()

    resp = client.get(f"/api/v1/challenges/{pending_challenge.id}/matches")
    assert resp.status_code == 400
    assert "Only validated challenges" in resp.json()["message"]


# ==============================================================================
# PHASE 2.4: CHALLENGE ASSIGNMENT & ACCEPTANCE
# ==============================================================================

def test_government_user_can_create_assignment(
    client: TestClient,
    govt_headers,
    validated_challenge,
    university_b,
):
    """8. Authorized government user can issue a challenge assignment."""
    payload = {
        "universityId": university_b.id,
        "invitation_message": "Mandate issued for rural groundwater purification.",
    }
    resp = client.post(
        f"/api/v1/challenges/{validated_challenge.id}/assignments",
        headers=govt_headers,
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["status"] == AssignmentStatus.INVITED.value
    assert data["challenge_id"] == validated_challenge.id
    assert data["university_id"] == university_b.id


def test_unauthorized_user_cannot_create_assignment(
    client: TestClient,
    citizen_headers,
    validated_challenge,
    university_b,
):
    """9. Citizens cannot issue challenge assignments."""
    payload = {"university_id": university_b.id}
    resp = client.post(
        f"/api/v1/challenges/{validated_challenge.id}/assignments",
        headers=citizen_headers,
        json=payload,
    )
    assert resp.status_code == 403


def test_university_admin_can_accept_assignment(
    client: TestClient,
    db_session,
    govt_user,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
):
    """10. University admin can accept its assignment."""
    assignment = ChallengeAssignment(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        assigned_by_user_id=govt_user.id,
        status=AssignmentStatus.INVITED,
    )
    db_session.add(assignment)
    db_session.commit()

    resp = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        headers=uni_admin_b_headers,
        json={"response_message": "Accepted with team of 5 faculty and 10 students."},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == AssignmentStatus.ACCEPTED.value


def test_university_cannot_accept_another_university_assignment(
    client: TestClient,
    db_session,
    govt_user,
    uni_admin_a_headers,
    validated_challenge,
    university_b,
):
    """11. University A admin cannot accept University B's assignment."""
    assignment = ChallengeAssignment(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        assigned_by_user_id=govt_user.id,
        status=AssignmentStatus.INVITED,
    )
    db_session.add(assignment)
    db_session.commit()

    resp = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        headers=uni_admin_a_headers,
    )
    assert resp.status_code == 403


def test_invalid_assignment_state_transition_rejected(
    client: TestClient,
    db_session,
    govt_user,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
):
    """12. An already DECLINED assignment cannot be accepted."""
    assignment = ChallengeAssignment(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        assigned_by_user_id=govt_user.id,
        status=AssignmentStatus.DECLINED,
    )
    db_session.add(assignment)
    db_session.commit()

    resp = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        headers=uni_admin_b_headers,
    )
    assert resp.status_code == 400


# ==============================================================================
# PHASE 2.5: PROJECT WORKSPACE
# ==============================================================================

def test_accepted_assignment_creates_one_project(
    client: TestClient,
    db_session,
    govt_user,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
):
    """13. Accepting an assignment automatically creates exactly one project."""
    assignment = ChallengeAssignment(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        assigned_by_user_id=govt_user.id,
        status=AssignmentStatus.INVITED,
    )
    db_session.add(assignment)
    db_session.commit()

    accept_resp = client.post(
        f"/api/v1/assignments/{assignment.id}/accept",
        headers=uni_admin_b_headers,
    )
    assert accept_resp.status_code == 200

    projects = db_session.query(Project).filter(Project.assignment_id == assignment.id).all()
    assert len(projects) == 1
    assert projects[0].status == ProjectStatus.ACTIVE
    assert projects[0].challenge_id == validated_challenge.id


def test_repeated_acceptance_idempotent_project_creation(
    client: TestClient,
    db_session,
    govt_user,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
):
    """14. Repeated acceptance calls do not create duplicate projects."""
    assignment = ChallengeAssignment(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        assigned_by_user_id=govt_user.id,
        status=AssignmentStatus.INVITED,
    )
    db_session.add(assignment)
    db_session.commit()

    client.post(f"/api/v1/assignments/{assignment.id}/accept", headers=uni_admin_b_headers)
    client.post(f"/api/v1/assignments/{assignment.id}/accept", headers=uni_admin_b_headers)

    count = db_session.query(Project).filter(Project.assignment_id == assignment.id).count()
    assert count == 1


def test_authorized_university_user_can_access_project(
    client: TestClient,
    db_session,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
    uni_admin_b,
):
    """15. Authorized university member can access project details."""
    proj = Project(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        title="Fluoride Removal Project Workspace",
        status=ProjectStatus.ACTIVE,
        created_by_user_id=uni_admin_b.id,
    )
    db_session.add(proj)
    db_session.commit()

    resp = client.get(f"/api/v1/projects/{proj.id}", headers=uni_admin_b_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Fluoride Removal Project Workspace"
    assert "progressPercentage" in data

    c_resp = client.get(f"/api/v1/challenges/{validated_challenge.id}/project", headers=uni_admin_b_headers)
    assert c_resp.status_code == 200
    assert c_resp.json()["id"] == proj.id


def test_unauthorized_user_cannot_access_private_project_data(
    client: TestClient,
    db_session,
    other_citizen_headers,
    validated_challenge,
    university_b,
    uni_admin_b,
):
    """16. Unauthorized citizen cannot access restricted project workspace details."""
    proj = Project(
        challenge_id=validated_challenge.id,
        university_id=university_b.id,
        title="Restricted R&D Workspace",
        status=ProjectStatus.ACTIVE,
        created_by_user_id=uni_admin_b.id,
    )
    db_session.add(proj)
    db_session.commit()

    resp = client.get(f"/api/v1/projects/{proj.id}", headers=other_citizen_headers)
    assert resp.status_code == 403


# ==============================================================================
# INTEGRATION & AUDIT
# ==============================================================================

def test_end_to_end_institutional_flow(
    client: TestClient,
    db_session,
    govt_headers,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
):
    """17. End-to-end flow: Validated challenge -> Match -> Assign -> Accept -> Project."""
    # 1. Matching
    match_resp = client.get(f"/api/v1/challenges/{validated_challenge.id}/matches")
    assert match_resp.status_code == 200
    matches = match_resp.json()["matches"]
    assert any(m["university_id"] == university_b.id for m in matches)

    # 2. Assignment via frontend alias
    assign_resp = client.post(
        f"/api/v1/challenges/{validated_challenge.id}/assign-hei",
        headers=govt_headers,
        json={"universityId": university_b.id},
    )
    assert assign_resp.status_code == 201
    assignment_id = assign_resp.json()["data"]["id"]

    # 3. Acceptance by university admin
    accept_resp = client.post(
        f"/api/v1/assignments/{assignment_id}/accept",
        headers=uni_admin_b_headers,
        json={"response_message": "Mandate accepted by Department of Civil Engineering."},
    )
    assert accept_resp.status_code == 200

    # 4. Project Workspace Query
    proj_resp = client.get(
        f"/api/v1/challenges/{validated_challenge.id}/project",
        headers=uni_admin_b_headers,
    )
    assert proj_resp.status_code == 200
    p_data = proj_resp.json()
    assert p_data["challenge_id"] == validated_challenge.id
    assert p_data["university_id"] == university_b.id
    assert p_data["status"] == ProjectStatus.ACTIVE.value


def test_notifications_and_audit_logs_created(
    client: TestClient,
    db_session,
    govt_headers,
    uni_admin_b_headers,
    validated_challenge,
    university_b,
    citizen_user,
):
    """18. Notifications and audit records are created across the assignment/project workflow."""
    assign_resp = client.post(
        f"/api/v1/challenges/{validated_challenge.id}/assignments",
        headers=govt_headers,
        json={"university_id": university_b.id},
    )
    assert assign_resp.status_code == 201
    assignment_id = assign_resp.json()["data"]["id"]

    uni_notif = db_session.query(Notification).filter(
        Notification.notification_type == NotificationType.DEPARTMENT_ASSIGNED
    ).first()
    assert uni_notif is not None

    client.post(
        f"/api/v1/assignments/{assignment_id}/accept",
        headers=uni_admin_b_headers,
    )

    citizen_notif = db_session.query(Notification).filter(
        Notification.recipient_user_id == citizen_user.id,
        Notification.title == "Project Workspace Created",
    ).first()
    assert citizen_notif is not None

    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.entity_type.in_(["challenge_assignment", "project"])
    ).all()
    assert len(audit_logs) >= 2
