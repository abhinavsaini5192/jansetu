"""
Phase 2.11 Final Integration Test Suite.
Verifies the complete JanSetu Phase 1 & Phase 2 lifecycle:
1. Application starts and health endpoint works.
2. Database migrations complete successfully.
3. User can register/login and access protected endpoint.
4. Citizen can submit a challenge and government can validate it.
5. Validated challenge can proceed through university assignment and acceptance.
6. Accepted assignment creates or connects to a project successfully.
7. Project workflow works through team/proposal/milestone/partner/risk creation.
8. Unauthorized user is blocked from accessing another project's private data.
"""
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.core.config import settings
from app.core.security import create_access_token
from app.models.attachment import Attachment
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.university_profile import UniversityProfile
from app.models.user import User
from app.utils.enums import (
    InstitutionCategory,
    OrganizationMembershipRole,
    OrganizationType,
    PartnerType,
    ProjectStatus,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
    SocietalDomain,
    SupportType,
    TeamRole,
    UserRole,
    ValidationStatus,
)


def auth_headers(user: User) -> dict:
    """Helper creating authorization headers with Bearer token."""
    token = create_access_token(
        subject=user.id,
        additional_claims={"email": user.email, "role": user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# 1. Application starts and health endpoint works
# ===========================================================================
def test_1_application_starts_and_health_endpoint_works(client: TestClient):
    """1. Verify application startup, healthcheck, and system status endpoints."""
    # Health endpoint
    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    data_health = resp_health.json()
    assert data_health["status"] in ("healthy", "degraded")
    assert "version" in data_health

    # System status endpoint
    resp_sys = client.get("/api/v1/system/status")
    assert resp_sys.status_code == 200
    data_sys = resp_sys.json()
    assert data_sys["success"] is True
    assert "database" in data_sys["data"]


# ===========================================================================
# 2. Database migrations complete successfully
# ===========================================================================
def test_2_database_migrations_complete_successfully(tmp_path, monkeypatch):
    """2. Verify that Alembic migrations upgrade cleanly from baseline to head."""
    from alembic import command
    from alembic.config import Config

    test_db = tmp_path / "alembic_integration_test.db"
    db_url = f"sqlite:///{test_db}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setattr(settings, "DATABASE_URL", db_url)

    ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
    cfg = Config(ini_path)
    cfg.set_main_option("sqlalchemy.url", db_url)

    # Run upgrade to head
    command.upgrade(cfg, "head")

    # Inspect created tables
    engine = create_engine(db_url)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        required_tables = {
            "users",
            "organizations",
            "organization_memberships",
            "challenges",
            "attachments",
            "government_reviews",
            "notifications",
            "audit_logs",
            "university_profiles",
            "departments",
            "capabilities",
            "department_capabilities",
            "challenge_assignments",
            "projects",
            "project_teams",
            "project_team_members",
            "proposals",
            "milestones",
            "deliverables",
            "project_partners",
            "partner_support",
            "project_risks",
            "project_activities",
        }
        for t in required_tables:
            assert t in tables, f"Missing table {t} after running migrations"
    finally:
        engine.dispose()


# ===========================================================================
# 3. User can register/login and access protected endpoint
# ===========================================================================
def test_3_user_can_register_login_and_access_protected_endpoint(client: TestClient):
    """3. Verify registration, token generation, and authenticated endpoint access."""
    email = f"citizen.{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword@123"

    # Register
    reg_payload = {
        "full_name": "Rohan Birsa",
        "email": email,
        "password": password,
        "role": "citizen",
    }
    resp_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert resp_reg.status_code == 201
    assert resp_reg.json()["success"] is True

    # Login
    login_payload = {
        "email": email,
        "password": password,
    }
    resp_login = client.post("/api/v1/auth/login", json=login_payload)
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    assert token

    # Access protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    resp_me = client.get("/api/v1/auth/me", headers=headers)
    assert resp_me.status_code == 200
    me_data = resp_me.json()
    assert me_data["email"] == email
    assert me_data["full_name"] == "Rohan Birsa"


# ===========================================================================
# 4. Citizen can submit a challenge and government can validate it
# ===========================================================================
def test_4_citizen_can_submit_challenge_and_government_can_validate_it(client: TestClient, db_session):
    """4. Verify citizen submission and government validation workflow."""
    # Create citizen
    citizen = User(
        full_name="Anjali Munda",
        email=f"anjali.{uuid.uuid4().hex[:6]}@example.com",
        password_hash="pass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    # Create government officer
    govt_officer = User(
        full_name="Rajesh Nodal",
        email=f"nodal.{uuid.uuid4().hex[:6]}@jharkhand.gov.in",
        password_hash="pass",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        is_active=True,
    )
    db_session.add_all([citizen, govt_officer])
    db_session.commit()

    # Citizen submits challenge
    challenge_payload = {
        "title": "Groundwater Arsenic Contamination in Sahibganj Riverbank",
        "description": "Arsenic concentration in 8 drinking tube-wells exceeds 0.05 mg/L.",
        "problem_statement": "Elevated arsenic in community groundwater sources requiring decentralized filtration.",
        "district": "Sahibganj",
        "domain": "water",
        "priority": "high",
        "urgency": "critical",
    }
    resp_sub = client.post("/api/v1/challenges", json=challenge_payload, headers=auth_headers(citizen))
    assert resp_sub.status_code == 201
    challenge_data = resp_sub.json()
    challenge_id = challenge_data["id"]
    assert challenge_data["status"] == "submitted"
    assert challenge_data["validation_status"] == "pending"

    # Government officer validates challenge
    review_payload = {
        "decision": "validate",
        "remarks": "Verified by District Public Health Engineering Department.",
        "department": "Drinking Water and Sanitation Department",
    }
    resp_val = client.post(
        f"/api/v1/government/challenges/{challenge_id}/validate",
        json=review_payload,
        headers=auth_headers(govt_officer),
    )
    assert resp_val.status_code == 200
    assert resp_val.json()["success"] is True

    # Verify updated challenge status
    resp_check = client.get(f"/api/v1/challenges/{challenge_id}")
    assert resp_check.status_code == 200
    data_check = resp_check.json()
    assert data_check["validation_status"] == ValidationStatus.VALIDATED.value


# ===========================================================================
# 5. Validated challenge proceeds through university assignment and acceptance
# ===========================================================================
def test_5_validated_challenge_can_proceed_through_university_assignment_and_acceptance(client: TestClient, db_session):
    """5. Verify matching, mandate assignment, and university acceptance."""
    # 1. Setup Government Officer
    govt_user = User(
        full_name="State Nodal Officer",
        email=f"nodal.{uuid.uuid4().hex[:6]}@gov.in",
        password_hash="pass",
        role=UserRole.STATE_NODAL_OFFICER,
        is_active=True,
    )
    # 2. Setup University & Admin
    uni_org = Organization(
        name=f"NIT Jamshedpur {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.UNIVERSITY,
        district="East Singhbhum",
        state="Jharkhand",
        is_active=True,
        is_verified=True,
    )
    db_session.add_all([govt_user, uni_org])
    db_session.flush()

    uni_prof = UniversityProfile(
        organization_id=uni_org.id,
        institution_category=InstitutionCategory.NIT,
        accreditation_details="NIRF Top 100",
        district="East Singhbhum",
        is_verified=True,
        is_active=True,
    )
    uni_admin = User(
        full_name="Prof. Sharma (Dean R&D)",
        email=f"dean.rd.{uuid.uuid4().hex[:6]}@nitjsr.ac.in",
        password_hash="pass",
        role=UserRole.UNIVERSITY_ADMIN,
        is_active=True,
    )
    db_session.add_all([uni_prof, uni_admin])
    db_session.flush()

    mem = OrganizationMembership(
        user_id=uni_admin.id,
        organization_id=uni_org.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    )
    # 3. Setup Validated Challenge
    citizen = User(
        full_name="Citizen Submitter",
        email=f"citizen.{uuid.uuid4().hex[:6]}@example.com",
        password_hash="pass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add_all([mem, citizen])
    db_session.commit()

    ch_resp = client.post(
        "/api/v1/challenges",
        json={
            "title": "Industrial Chromium Effluent in Damodar Basin",
            "description": "Effluent discharge exceeding hexavalent chromium statutory limits.",
            "problem_statement": "Remediation of industrial chromium runoff through electrocoagulation.",
            "district": "East Singhbhum",
            "domain": "environment",
        },
        headers=auth_headers(citizen),
    )
    challenge_id = ch_resp.json()["id"]

    # Validate challenge
    client.post(
        f"/api/v1/government/challenges/{challenge_id}/validate",
        json={"remarks": "Confirmed by State Pollution Control Board."},
        headers=auth_headers(govt_user),
    )

    # 4. View matches
    resp_matches = client.get(f"/api/v1/challenges/{challenge_id}/matches")
    assert resp_matches.status_code == 200
    assert "matches" in resp_matches.json()

    # 5. Issue Assignment Mandate
    resp_assign = client.post(
        f"/api/v1/challenges/{challenge_id}/assignments",
        json={
            "university_id": uni_org.id,
            "mandate_notes": "Formal mandate to develop an electrocoagulation filtration prototype.",
        },
        headers=auth_headers(govt_user),
    )
    assert resp_assign.status_code == 201
    assign_id = resp_assign.json()["data"]["id"]

    # 6. University Admin Accepts Assignment
    resp_accept = client.post(
        f"/api/v1/assignments/{assign_id}/accept",
        headers=auth_headers(uni_admin),
    )
    assert resp_accept.status_code == 200
    data_acc = resp_accept.json()
    assert data_acc["success"] is True
    assert data_acc["data"]["status"] == "accepted"


# ===========================================================================
# 6. Accepted assignment creates or connects to project successfully
# ===========================================================================
def test_6_accepted_assignment_creates_or_connects_to_project_successfully(client: TestClient, db_session):
    """6. Verify automated project workspace creation on mandate acceptance."""
    govt_user = User(
        full_name="Officer Verma",
        email=f"officer.{uuid.uuid4().hex[:6]}@gov.in",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        password_hash="pass",
        is_active=True,
    )
    uni_org = Organization(
        name=f"IIT ISM Dhanbad {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Dhanbad",
        is_active=True,
        is_verified=True,
    )
    db_session.add_all([govt_user, uni_org])
    db_session.flush()

    uni_prof = UniversityProfile(
        organization_id=uni_org.id,
        institution_category=InstitutionCategory.IIT,
        district="Dhanbad",
        is_active=True,
        is_verified=True,
    )
    uni_admin = User(
        full_name="IIT Dean Academic",
        email=f"dean.{uuid.uuid4().hex[:6]}@iitism.ac.in",
        role=UserRole.UNIVERSITY_ADMIN,
        password_hash="pass",
        is_active=True,
    )
    db_session.add_all([uni_prof, uni_admin])
    db_session.flush()

    db_session.add(OrganizationMembership(
        user_id=uni_admin.id,
        organization_id=uni_org.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    ))
    citizen = User(
        full_name="Villager Sunita",
        email=f"sunita.{uuid.uuid4().hex[:6]}@example.com",
        role=UserRole.CITIZEN,
        password_hash="pass",
        is_active=True,
    )
    db_session.add(citizen)
    db_session.commit()

    # Submit & Validate challenge
    resp_ch = client.post(
        "/api/v1/challenges",
        json={"title": "Methane Seepage in Coal Bed Blocks", "problem_statement": "Methane detection in village wells.", "district": "Dhanbad", "domain": "energy"},
        headers=auth_headers(citizen),
    )
    ch_id = resp_ch.json()["id"]
    client.post(f"/api/v1/government/challenges/{ch_id}/validate", json={"remarks": "Validated"}, headers=auth_headers(govt_user))

    # Assign & Accept
    resp_as = client.post(
        f"/api/v1/challenges/{ch_id}/assignments",
        json={"university_id": uni_org.id},
        headers=auth_headers(govt_user),
    )
    assign_id = resp_as.json()["data"]["id"]
    client.post(f"/api/v1/assignments/{assign_id}/accept", headers=auth_headers(uni_admin))

    # Verify project exists via challenge project endpoint
    resp_prj = client.get(f"/api/v1/challenges/{ch_id}/project", headers=auth_headers(uni_admin))
    assert resp_prj.status_code == 200
    prj_data = resp_prj.json()
    assert prj_data["project_code"].startswith("PRJ-")
    assert prj_data["status"] == ProjectStatus.ACTIVE.value
    assert prj_data["university_id"] == uni_org.id


# ===========================================================================
# 7. Project workflow works through team/proposal/milestone/partner/risk creation
# ===========================================================================
def test_7_project_workflow_works_through_team_proposal_milestone_partner_risk_creation(client: TestClient, db_session):
    """7. Full collaboration flow: Teams, Proposals, Milestones, Deliverables, Partners, Risks & Timeline."""
    # Setup University, Faculty Lead, Student, Partner, Nodal Officer
    uni_org = Organization(
        name=f"Birsa University {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Ranchi",
        is_active=True,
        is_verified=True,
    )
    partner_org = Organization(
        name=f"Tata Steel CSR {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.INDUSTRY,
        district="East Singhbhum",
        is_active=True,
        is_verified=True,
    )
    db_session.add_all([uni_org, partner_org])
    db_session.flush()

    faculty = User(
        full_name="Dr. Arvind Pandey",
        email=f"arvind.{uuid.uuid4().hex[:6]}@birsa.ac.in",
        role=UserRole.FACULTY,
        password_hash="pass",
        is_active=True,
    )
    student = User(
        full_name="Neha Kumari",
        email=f"neha.{uuid.uuid4().hex[:6]}@birsa.ac.in",
        role=UserRole.STUDENT,
        password_hash="pass",
        is_active=True,
    )
    partner_admin = User(
        full_name="Sanjay Corporate Lead",
        email=f"sanjay.{uuid.uuid4().hex[:6]}@tatasteel.com",
        role=UserRole.CSR_PARTNER,
        password_hash="pass",
        is_active=True,
    )
    nodal = User(
        full_name="Nodal Officer Ranchi",
        email=f"nodal.{uuid.uuid4().hex[:6]}@gov.in",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        password_hash="pass",
        is_active=True,
    )
    db_session.add_all([faculty, student, partner_admin, nodal])
    db_session.flush()

    # Memberships
    db_session.add(OrganizationMembership(user_id=faculty.id, organization_id=uni_org.id, membership_role=OrganizationMembershipRole.ADMIN, is_active=True))
    db_session.add(OrganizationMembership(user_id=student.id, organization_id=uni_org.id, membership_role=OrganizationMembershipRole.MEMBER, is_active=True))
    db_session.add(OrganizationMembership(user_id=partner_admin.id, organization_id=partner_org.id, membership_role=OrganizationMembershipRole.ADMIN, is_active=True))
    db_session.commit()

    headers_fac = auth_headers(faculty)
    headers_nodal = auth_headers(nodal)
    headers_part = auth_headers(partner_admin)

    # Initialize Project directly
    from app.models.challenge import Challenge
    from app.models.project import Project

    challenge = Challenge(
        submitted_by_user_id=faculty.id,
        title="Decentralized Biomass Gasifier for Rural Electrification",
        description="Providing 24/7 power to off-grid tribal villages.",
        problem_statement="Off-grid power generation using agricultural waste pellets.",
        district="Ranchi",
        domain="energy",
        status="assigned",
        validation_status="validated",
    )
    db_session.add(challenge)
    db_session.flush()

    project = Project(
        project_code=f"PRJ-2026-{uuid.uuid4().hex[:6].upper()}",
        challenge_id=challenge.id,
        university_id=uni_org.id,
        title="Biomass Gasifier Engineering Workspace",
        created_by_user_id=faculty.id,
        status=ProjectStatus.ACTIVE,
    )
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    # 1. Create Team & Add Member (Phase 2.6)
    resp_team = client.post(
        f"/api/v1/projects/{project_id}/teams",
        json={"name": "Gasifier Fabrication Unit", "description": "Mechanical & electrical fabrication team."},
        headers=headers_fac,
    )
    assert resp_team.status_code == 201
    team_id = resp_team.json()["id"]

    resp_add_m = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": student.id, "role": "student"},
        headers=headers_fac,
    )
    assert resp_add_m.status_code == 201

    # 2. Create, Submit & Approve Proposal (Phase 2.7)
    resp_prop = client.post(
        f"/api/v1/projects/{project_id}/proposals",
        json={
            "title": "Biomass Gasifier Technical Blueprint v1.0",
            "summary": "Downdraft gasifier with cyclone dust separator and gas cooling array.",
            "methodology": "Fabrication using local mild steel and testing with rice husk fuel pellets.",
            "estimated_budget": "INR 4,50,000",
        },
        headers=headers_fac,
    )
    assert resp_prop.status_code == 201
    prop_id = resp_prop.json()["id"]

    resp_sub_prop = client.post(f"/api/v1/proposals/{prop_id}/submit", headers=headers_fac)
    assert resp_sub_prop.status_code == 200

    resp_app_prop = client.post(
        f"/api/v1/proposals/{prop_id}/review",
        json={"decision": "approve", "review_notes": "Technical blueprint conforms to rural energy safety standards."},
        headers=headers_nodal,
    )
    assert resp_app_prop.status_code == 200
    assert resp_app_prop.json()["status"] == "approved"

    # 3. Create Milestone & Submit Deliverable (Phase 2.8)
    resp_ms = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={"title": "Reactor Chamber Welding & Assembly", "sequence_number": 1},
        headers=headers_fac,
    )
    assert resp_ms.status_code == 201
    ms_id = resp_ms.json()["id"]

    # Sample attachment in DB
    att = Attachment(
        challenge_id=challenge.id,
        uploaded_by_user_id=faculty.id,
        original_filename="welding_inspection_cert.pdf",
        stored_filename=f"{uuid.uuid4().hex}_welding_inspection_cert.pdf",
        storage_path="/uploads/test/welding_inspection_cert.pdf",
        mime_type="application/pdf",
        file_size=128000,
        file_extension="pdf",
    )
    db_session.add(att)
    db_session.commit()

    resp_del = client.post(
        f"/api/v1/milestones/{ms_id}/deliverables",
        json={
            "title": "Chamber Hydrostatic Test Certificate",
            "description": "Pressure vessel certified leak-free up to 2.5 bar operating pressure.",
            "file_attachment_id": att.id,
        },
        headers=headers_fac,
    )
    assert resp_del.status_code == 201

    # 4. Invite Partner, Accept & Add Support (Phase 2.9)
    resp_inv = client.post(
        f"/api/v1/projects/{project_id}/partners/invite",
        json={"organization_id": partner_org.id, "partner_type": "csr", "invitation_message": "Inviting Tata CSR for field deployment support."},
        headers=headers_fac,
    )
    assert resp_inv.status_code == 201
    partner_id = resp_inv.json()["id"]

    resp_acc_part = client.post(f"/api/v1/project-partners/{partner_id}/accept", headers=headers_part)
    assert resp_acc_part.status_code == 200
    assert resp_acc_part.json()["status"] == "accepted"

    resp_supp = client.post(
        f"/api/v1/project-partners/{partner_id}/support",
        json={"support_type": "funding", "description": "Direct CSR grant for field deployment materials", "estimated_value": "INR 2,00,000"},
        headers=headers_part,
    )
    assert resp_supp.status_code == 201

    # 5. Create & Resolve Risk (Phase 2.10)
    resp_risk = client.post(
        f"/api/v1/projects/{project_id}/risks",
        json={
            "title": "Feedstock Seasonal Shortage",
            "description": "Rice husk unavailability during monsoon sowing season.",
            "severity": "high",
            "likelihood": "medium",
            "mitigation_plan": "Establish multi-fuel capability supporting dried pine needles and bamboo leaves.",
        },
        headers=headers_fac,
    )
    assert resp_risk.status_code == 201
    risk_id = resp_risk.json()["id"]
    # High (3) * Medium (2) = 6
    assert resp_risk.json()["risk_score"] == 6

    resp_res_risk = client.post(
        f"/api/v1/risks/{risk_id}/resolve",
        json={"resolution_notes": "Multi-fuel testing verified with pine needle briquettes."},
        headers=headers_fac,
    )
    assert resp_res_risk.status_code == 200
    assert resp_res_risk.json()["status"] == RiskStatus.RESOLVED.value

    # 6. Verify Timeline & Activity Logs (Phase 2.10)
    resp_tl = client.get(f"/api/v1/projects/{project_id}/timeline", headers=headers_fac)
    assert resp_tl.status_code == 200
    tl_data = resp_tl.json()
    assert tl_data["success"] is True
    assert len(tl_data["data"]) >= 5


# ===========================================================================
# 8. Unauthorized user is blocked from accessing another project's private data
# ===========================================================================
def test_8_unauthorized_user_is_blocked_from_accessing_another_projects_private_data(client: TestClient, db_session):
    """8. Verify strict RBAC isolation prevents unauthorized viewing or tampering."""
    # Create Organization and Project
    uni_org = Organization(
        name=f"Central University {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Ranchi",
        is_active=True,
    )
    db_session.add(uni_org)
    db_session.flush()

    lead_user = User(
        full_name="Lead Professor",
        email=f"prof.{uuid.uuid4().hex[:6]}@central.ac.in",
        role=UserRole.FACULTY,
        password_hash="pass",
        is_active=True,
    )
    stranger_user = User(
        full_name="Stranger Citizen",
        email=f"stranger.{uuid.uuid4().hex[:6]}@other.com",
        role=UserRole.CITIZEN,
        password_hash="pass",
        is_active=True,
    )
    db_session.add_all([lead_user, stranger_user])
    db_session.flush()

    db_session.add(OrganizationMembership(user_id=lead_user.id, organization_id=uni_org.id, membership_role=OrganizationMembershipRole.ADMIN, is_active=True))

    from app.models.challenge import Challenge
    from app.models.project import Project

    challenge = Challenge(
        submitted_by_user_id=lead_user.id,
        title="Protected Challenge",
        district="Ranchi",
        domain="health",
    )
    db_session.add(challenge)
    db_session.flush()

    project = Project(
        project_code=f"PRJ-2026-{uuid.uuid4().hex[:6].upper()}",
        challenge_id=challenge.id,
        university_id=uni_org.id,
        title="Classified Medical Diagnostic Project",
        created_by_user_id=lead_user.id,
        status=ProjectStatus.ACTIVE,
    )
    db_session.add(project)
    db_session.commit()

    headers_stranger = auth_headers(stranger_user)

    # 1. Unrelated user blocked from timeline
    resp_tl = client.get(f"/api/v1/projects/{project.id}/timeline", headers=headers_stranger)
    assert resp_tl.status_code == 403

    # 2. Unrelated user blocked from creating team
    resp_team = client.post(
        f"/api/v1/projects/{project.id}/teams",
        json={"name": "Intruder Team"},
        headers=headers_stranger,
    )
    assert resp_team.status_code == 403

    # 3. Unrelated user blocked from creating risk
    resp_risk = client.post(
        f"/api/v1/projects/{project.id}/risks",
        json={"title": "Unauthorized Risk", "severity": "low", "likelihood": "low"},
        headers=headers_stranger,
    )
    assert resp_risk.status_code == 403
