"""
Comprehensive Test Suite for JanSetu Phases 2.6 – 2.10:
Institutional Collaboration & Project Lifecycle Workflow.

Covers:
- Phase 2.6: Team Management (teams, member roles, duplicate member guards, team lead deactivation safeguards)
- Phase 2.7: Proposal Management (creation, submission, review transitions, history tracking, permission isolation)
- Phase 2.8: Milestones & Deliverables (creation, progress calculations, deliverable submission with attachments, reviews)
- Phase 2.9: Industry & CSR Collaboration (partner invitation, acceptance/decline, support offers, permission isolation)
- Phase 2.10: Project Risks & Activity Timeline (risk score calculation, resolution, automatic activity recording, timeline pagination)
- End-to-End Collaboration Integration: Full project lifecycle from team formation to milestone deliverable and partner onboarding
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.challenge import Challenge
from app.models.deliverable import Deliverable
from app.models.milestone import Milestone
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.partner_support import PartnerSupport
from app.models.project import Project
from app.models.project_activity import ProjectActivity
from app.models.project_partner import ProjectPartner
from app.models.project_risk import ProjectRisk
from app.models.project_team import ProjectTeam
from app.models.project_team_member import ProjectTeamMember
from app.models.proposal import Proposal
from app.models.user import User
from app.utils.enums import (
    AuditAction,
    ChallengeStatus,
    DeliverableStatus,
    MilestoneStatus,
    OrganizationMembershipRole,
    OrganizationType,
    PartnerStatus,
    PartnerType,
    PriorityLevel,
    ProjectActivityType,
    ProjectStatus,
    ProposalStatus,
    RiskLikelihood,
    RiskSeverity,
    RiskStatus,
    SocietalDomain,
    SupportStatus,
    SupportType,
    TeamRole,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


def auth_headers(user: User) -> dict:
    token = create_access_token(
        subject=user.id,
        additional_claims={"email": user.email, "role": user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def platform_admin(db_session) -> User:
    user = User(
        full_name="Platform Admin",
        email=f"admin.{uuid.uuid4().hex[:6]}@jansetu.gov.in",
        password_hash="hashedpass",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def govt_officer(db_session) -> User:
    user = User(
        full_name="District Nodal Officer",
        email=f"nodal.{uuid.uuid4().hex[:6]}@jharkhand.gov.in",
        password_hash="hashedpass",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_user(db_session) -> User:
    user = User(
        full_name="Ramesh Soren",
        email=f"citizen.{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def university_org(db_session) -> Organization:
    org = Organization(
        name=f"Birsa Institute of Technology Sindri {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.UNIVERSITY,
        district="Dhanbad",
        state="Jharkhand",
        is_verified=True,
        is_active=True,
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def faculty_lead(db_session, university_org) -> User:
    user = User(
        full_name="Dr. Alok Verma",
        email=f"faculty.{uuid.uuid4().hex[:6]}@bit-sindri.ac.in",
        password_hash="hashedpass",
        role=UserRole.FACULTY,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    mem = OrganizationMembership(
        user_id=user.id,
        organization_id=university_org.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    )
    db_session.add(mem)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session, university_org) -> User:
    user = User(
        full_name="Priya Kumari",
        email=f"student.{uuid.uuid4().hex[:6]}@bit-sindri.ac.in",
        password_hash="hashedpass",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    mem = OrganizationMembership(
        user_id=user.id,
        organization_id=university_org.id,
        membership_role=OrganizationMembershipRole.MEMBER,
        is_active=True,
    )
    db_session.add(mem)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user_2(db_session, university_org) -> User:
    user = User(
        full_name="Amit Mahato",
        email=f"student2.{uuid.uuid4().hex[:6]}@bit-sindri.ac.in",
        password_hash="hashedpass",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    mem = OrganizationMembership(
        user_id=user.id,
        organization_id=university_org.id,
        membership_role=OrganizationMembershipRole.MEMBER,
        is_active=True,
    )
    db_session.add(mem)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def industry_org(db_session) -> Organization:
    org = Organization(
        name=f"Tata Steel Rural Development Society {uuid.uuid4().hex[:4]}",
        organization_type=OrganizationType.INDUSTRY,
        district="East Singhbhum",
        state="Jharkhand",
        is_verified=True,
        is_active=True,
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def industry_admin(db_session, industry_org) -> User:
    user = User(
        full_name="Sunil Agrawal",
        email=f"csr.{uuid.uuid4().hex[:6]}@tatasteel.com",
        password_hash="hashedpass",
        role=UserRole.CSR_PARTNER,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    mem = OrganizationMembership(
        user_id=user.id,
        organization_id=industry_org.id,
        membership_role=OrganizationMembershipRole.ADMIN,
        is_active=True,
    )
    db_session.add(mem)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def active_project(db_session, citizen_user, university_org, faculty_lead) -> Project:
    challenge = Challenge(
        submitted_by_user_id=citizen_user.id,
        title="Solar Water Desalination for Fluoride-hit Dhanbad Blocks",
        description="Community drinking water sources in 12 villages have fluoride concentration exceeding 3.5 mg/L.",
        problem_statement="Drinking water exceeds permissible fluoride limits requiring low-cost filtration.",
        domain=SocietalDomain.WATER,
        district="Dhanbad",
        status=ChallengeStatus.ASSIGNED,
        validation_status=ValidationStatus.VALIDATED,
        priority=PriorityLevel.HIGH,
        urgency=UrgencyLevel.CRITICAL,
    )
    db_session.add(challenge)
    db_session.flush()

    project = Project(
        challenge_id=challenge.id,
        university_id=university_org.id,
        title="Solar Powered Water Purification Project",
        description="Engineering decentralized solar distillation units with activated alumina filtration.",
        status=ProjectStatus.ACTIVE,
        created_by_user_id=faculty_lead.id,
        lead_faculty="Dr. Alok Verma",
        budget="INR 8,50,000",
        progress_percentage=0,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


# ===========================================================================
# PART A: TEAM MANAGEMENT (Phase 2.6)
# ===========================================================================

def test_authorized_project_member_can_create_team(client: TestClient, faculty_lead, active_project, db_session):
    """1. Authorized university project authority can create a team and becomes team lead."""
    headers = auth_headers(faculty_lead)
    payload = {
        "name": "CleanWater Engineering Roster",
        "description": "Multidisciplinary roster of chemical and mechanical engineering students",
    }
    resp = client.post(f"/api/v1/projects/{active_project.id}/teams", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["project_id"] == active_project.id
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == faculty_lead.id
    assert data["members"][0]["role"] == TeamRole.TEAM_LEAD.value


def test_unauthorized_user_cannot_modify_team_membership(client: TestClient, citizen_user, faculty_lead, student_user, active_project, db_session):
    """2. Citizen or unrelated user cannot add members or alter team composition."""
    # First create team via faculty lead
    team = ProjectTeam(
        project_id=active_project.id,
        name="Telemetry Team",
        created_by_user_id=faculty_lead.id,
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    # Attempt addition as citizen
    headers = auth_headers(citizen_user)
    payload = {"user_id": student_user.id, "role": "student"}
    resp = client.post(f"/api/v1/teams/{team.id}/members", json=payload, headers=headers)
    assert resp.status_code == 403


def test_duplicate_team_membership_rejected(client: TestClient, faculty_lead, student_user, active_project, db_session):
    """3. Adding the same active user to a team twice returns 409 Conflict."""
    headers = auth_headers(faculty_lead)
    resp_team = client.post(
        f"/api/v1/projects/{active_project.id}/teams",
        json={"name": "Filtration Mechanics"},
        headers=headers,
    )
    team_id = resp_team.json()["id"]

    # First add succeeds
    resp1 = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": student_user.id, "role": "student"},
        headers=headers,
    )
    assert resp1.status_code == 201

    # Second add of same active user fails
    resp2 = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": student_user.id, "role": "student"},
        headers=headers,
    )
    assert resp2.status_code == 409


def test_removing_last_team_lead_rejected(client: TestClient, faculty_lead, active_project, db_session):
    """4. Removing or demoting the only team lead without designated replacement is rejected."""
    headers = auth_headers(faculty_lead)
    resp_team = client.post(
        f"/api/v1/projects/{active_project.id}/teams",
        json={"name": "Desalination Unit Team"},
        headers=headers,
    )
    team_id = resp_team.json()["id"]
    lead_member_id = resp_team.json()["members"][0]["id"]

    # Attempt to demote the sole team lead
    resp_demote = client.patch(
        f"/api/v1/teams/{team_id}/members/{lead_member_id}",
        json={"role": "contributor"},
        headers=headers,
    )
    assert resp_demote.status_code == 400
    err_body = resp_demote.json()
    err_msg = err_body.get("message") or err_body.get("detail", "")
    assert "lead" in err_msg.lower()

    # Attempt to delete the sole team lead
    resp_del = client.delete(
        f"/api/v1/teams/{team_id}/members/{lead_member_id}",
        headers=headers,
    )
    assert resp_del.status_code == 400


# ===========================================================================
# PART B: PROPOSAL MANAGEMENT (Phase 2.7)
# ===========================================================================

def test_team_member_can_create_and_submit_proposal(client: TestClient, faculty_lead, active_project, db_session):
    """5. Authorized university team lead can draft and submit a detailed technical proposal."""
    headers = auth_headers(faculty_lead)
    payload = {
        "title": "Low-Cost Solar Defluoridation Plant Blueprint",
        "summary": "Engineering a 500L/day continuous flow defluoridation reactor powered by solar thermal arrays.",
        "detailed_description": "Combines locally sourced activated alumina with parabolic trough solar concentrators to regenerate filtration beds without grid power.",
        "methodology": "Phase 1: Laboratory bench scale testing. Phase 2: Pilot prototype in Govindpur block.",
        "expected_outcomes": "Reduction of drinking water fluoride levels from 3.8 mg/L to below WHO permissible 1.0 mg/L for 600 villagers.",
        "estimated_budget": "INR 4,50,000",
    }
    resp = client.post(f"/api/v1/projects/{active_project.id}/proposals", json=payload, headers=headers)
    assert resp.status_code == 201
    prop = resp.json()
    assert prop["status"] == ProposalStatus.DRAFT.value
    assert prop["title"] == payload["title"]

    # Submit proposal
    resp_sub = client.post(f"/api/v1/proposals/{prop['id']}/submit", headers=headers)
    assert resp_sub.status_code == 200
    assert resp_sub.json()["status"] == ProposalStatus.SUBMITTED.value


def test_unauthorized_user_cannot_review_proposal(client: TestClient, student_user, faculty_lead, active_project, db_session):
    """6. Students and university members cannot review or approve their own proposals."""
    headers_fac = auth_headers(faculty_lead)
    resp_prop = client.post(
        f"/api/v1/projects/{active_project.id}/proposals",
        json={
            "title": "Prototype Blueprint",
            "summary": "Engineering blueprint summary for purification",
            "detailed_description": "Full technical breakdown for the purification methodology",
        },
        headers=headers_fac,
    )
    prop_id = resp_prop.json()["id"]
    client.post(f"/api/v1/proposals/{prop_id}/submit", headers=headers_fac)

    # Student attempts review
    headers_stu = auth_headers(student_user)
    resp_rev = client.post(
        f"/api/v1/proposals/{prop_id}/review",
        json={"decision": "approve", "review_comment": "Self approval"},
        headers=headers_stu,
    )
    assert resp_rev.status_code == 403


def test_valid_proposal_review_transitions(client: TestClient, govt_officer, faculty_lead, active_project, db_session):
    """7. Government officer reviews proposal: request revision, resubmit, and final approve."""
    headers_fac = auth_headers(faculty_lead)
    headers_govt = auth_headers(govt_officer)

    # 1. Create and submit
    resp_create = client.post(
        f"/api/v1/projects/{active_project.id}/proposals",
        json={
            "title": "Water Treatment Methodology",
            "summary": "Technical methodology summary for water treatment",
            "detailed_description": "Detailed chemical breakdown of the filtration system",
        },
        headers=headers_fac,
    )
    prop_id = resp_create.json()["id"]
    client.post(f"/api/v1/proposals/{prop_id}/submit", headers=headers_fac)

    # 2. Govt requests revision
    resp_rev1 = client.post(
        f"/api/v1/proposals/{prop_id}/review",
        json={"decision": "request_revision", "review_comment": "Please specify waste alumina disposal protocol."},
        headers=headers_govt,
    )
    assert resp_rev1.status_code == 200
    assert resp_rev1.json()["status"] == ProposalStatus.NEEDS_REVISION.value

    # 3. Faculty updates and resubmits
    client.patch(
        f"/api/v1/proposals/{prop_id}",
        json={"methodology": "Spent alumina will be neutralized and calcined for safe brick manufacturing incorporation."},
        headers=headers_fac,
    )
    resp_resub = client.post(f"/api/v1/proposals/{prop_id}/submit", headers=headers_fac)
    assert resp_resub.status_code == 200
    assert resp_resub.json()["status"] == ProposalStatus.SUBMITTED.value

    # 4. Govt approves
    resp_app = client.post(
        f"/api/v1/proposals/{prop_id}/review",
        json={"decision": "approve", "review_comment": "Approved for prototyping phase."},
        headers=headers_govt,
    )
    assert resp_app.status_code == 200
    assert resp_app.json()["status"] == ProposalStatus.APPROVED.value

    # 5. Check proposal history
    resp_hist = client.get(f"/api/v1/proposals/{prop_id}/history", headers=headers_fac)
    assert resp_hist.status_code == 200
    assert len(resp_hist.json()) >= 3


# ===========================================================================
# PART C: MILESTONES & DELIVERABLES (Phase 2.8)
# ===========================================================================

def test_authorized_team_member_can_create_milestone(client: TestClient, faculty_lead, active_project, db_session):
    """8. Authorized team member can define milestones and observe progress calculations."""
    headers = auth_headers(faculty_lead)
    payload = {
        "title": "Baseline Ground-Truth Testing",
        "description": "Collect water samples from 12 Dhanbad villages and establish baseline fluoride spectra.",
        "sequence_number": 1,
        "completion_percentage": 50,
    }
    resp = client.post(f"/api/v1/projects/{active_project.id}/milestones", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["completion_percentage"] == 50
    assert data["status"] == MilestoneStatus.IN_PROGRESS.value

    # Check overall project progress updated automatically
    db_session.refresh(active_project)
    assert active_project.progress_percentage == 50


def test_invalid_completion_percentage_rejected(client: TestClient, faculty_lead, active_project):
    """9. Milestone progress < 0 or > 100 is rejected with 422/400 validation error."""
    headers = auth_headers(faculty_lead)
    resp = client.post(
        f"/api/v1/projects/{active_project.id}/milestones",
        json={"title": "Invalid Progress Milestone", "completion_percentage": 150},
        headers=headers,
    )
    assert resp.status_code in (400, 422)


def test_deliverable_submission_and_review_workflow(client: TestClient, faculty_lead, govt_officer, active_project, db_session):
    """10. Deliverable submitted linking attachment and officially approved by authority."""
    headers_fac = auth_headers(faculty_lead)
    headers_govt = auth_headers(govt_officer)

    # 1. Create milestone
    resp_m = client.post(
        f"/api/v1/projects/{active_project.id}/milestones",
        json={"title": "Laboratory Spectrometry", "sequence_number": 1},
        headers=headers_fac,
    )
    milestone_id = resp_m.json()["id"]

    # 2. Create sample attachment in db
    att = Attachment(
        challenge_id=active_project.challenge_id,
        uploaded_by_user_id=faculty_lead.id,
        original_filename="spectrometry_analysis_report.pdf",
        stored_filename=f"{uuid.uuid4().hex}_spectrometry_analysis_report.pdf",
        storage_path="/uploads/test/spectrometry_analysis_report.pdf",
        mime_type="application/pdf",
        file_size=245000,
        file_extension="pdf",
    )
    db_session.add(att)
    db_session.commit()
    db_session.refresh(att)

    # 3. Submit deliverable
    resp_del = client.post(
        f"/api/v1/milestones/{milestone_id}/deliverables",
        json={
            "title": "Fluoride ICP-MS Spectrometry Analysis Report",
            "description": "Mass spectrometry data confirming 82% fluoride removal efficiency.",
            "file_attachment_id": att.id,
        },
        headers=headers_fac,
    )
    assert resp_del.status_code == 201
    deliverable_id = resp_del.json()["id"]
    assert resp_del.json()["status"] == DeliverableStatus.SUBMITTED.value

    # 4. Government officer reviews deliverable
    resp_rev = client.post(
        f"/api/v1/deliverables/{deliverable_id}/review",
        json={"decision": "accept", "review_comment": "Spectrometry charts verified and accepted."},
        headers=headers_govt,
    )
    assert resp_rev.status_code == 200
    assert resp_rev.json()["status"] == DeliverableStatus.ACCEPTED.value


# ===========================================================================
# PART D: INDUSTRY & CSR COLLABORATION (Phase 2.9)
# ===========================================================================

def test_authorized_user_can_invite_partner(client: TestClient, faculty_lead, industry_org, active_project):
    """11. University lead can invite industry/CSR partner organization."""
    headers = auth_headers(faculty_lead)
    payload = {
        "organization_id": industry_org.id,
        "partner_type": "csr",
        "invitation_message": "Inviting Tata Steel CSR to support prototype deployment in Govindpur.",
    }
    resp = client.post(f"/api/v1/projects/{active_project.id}/partners/invite", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["organization_id"] == industry_org.id
    assert data["status"] == PartnerStatus.INVITED.value
    assert data["partner_type"] == PartnerType.CSR.value


def test_partner_admin_can_accept_invitation(client: TestClient, faculty_lead, industry_org, industry_admin, active_project):
    """12. Industry/CSR admin accepts invitation for their organization."""
    headers_fac = auth_headers(faculty_lead)
    resp_inv = client.post(
        f"/api/v1/projects/{active_project.id}/partners/invite",
        json={"organization_id": industry_org.id, "partner_type": "csr"},
        headers=headers_fac,
    )
    partner_id = resp_inv.json()["id"]

    # Partner admin accepts
    headers_csr = auth_headers(industry_admin)
    resp_acc = client.post(
        f"/api/v1/project-partners/{partner_id}/accept",
        json={"decision": "accept", "response_message": "Tata Steel CSR is pleased to partner on this water initiative."},
        headers=headers_csr,
    )
    assert resp_acc.status_code == 200
    assert resp_acc.json()["status"] == PartnerStatus.ACCEPTED.value


def test_duplicate_active_partnerships_rejected(client: TestClient, faculty_lead, industry_org, active_project):
    """13. Inviting the same organization twice to a project returns 409 Conflict."""
    headers = auth_headers(faculty_lead)
    client.post(
        f"/api/v1/projects/{active_project.id}/partners/invite",
        json={"organization_id": industry_org.id, "partner_type": "csr"},
        headers=headers,
    )
    # Duplicate invite
    resp_dup = client.post(
        f"/api/v1/projects/{active_project.id}/partners/invite",
        json={"organization_id": industry_org.id, "partner_type": "csr"},
        headers=headers,
    )
    assert resp_dup.status_code == 409


def test_partner_support_offer_and_permission_isolation(client: TestClient, faculty_lead, student_user, industry_org, industry_admin, active_project):
    """14. Partner registers resource support offer; student or non-admin cannot update it."""
    headers_fac = auth_headers(faculty_lead)
    headers_csr = auth_headers(industry_admin)

    resp_inv = client.post(
        f"/api/v1/projects/{active_project.id}/partners/invite",
        json={"organization_id": industry_org.id, "partner_type": "csr"},
        headers=headers_fac,
    )
    partner_id = resp_inv.json()["id"]
    client.post(f"/api/v1/project-partners/{partner_id}/accept", headers=headers_csr)

    # CSR partner registers grant support offer
    support_payload = {
        "support_type": "funding",
        "description": "CSR Capital Equipment Grant for Parabolic Collectors",
        "estimated_value": "INR 3,00,000",
    }
    resp_sup = client.post(f"/api/v1/project-partners/{partner_id}/support", json=support_payload, headers=headers_csr)
    assert resp_sup.status_code == 201
    support_id = resp_sup.json()["id"]
    assert resp_sup.json()["support_type"] == SupportType.FUNDING.value

    # Student attempts to modify support offer
    headers_stu = auth_headers(student_user)
    resp_tamper = client.patch(
        f"/api/v1/partner-support/{support_id}",
        json={"estimated_value": "INR 50,00,000"},
        headers=headers_stu,
    )
    assert resp_tamper.status_code == 403


# ===========================================================================
# PART E: PROJECT RISKS & ACTIVITY TIMELINE (Phase 2.10)
# ===========================================================================

def test_create_project_risk_with_deterministic_score(client: TestClient, faculty_lead, active_project):
    """15. Risk score is computed transparently and deterministically (severity * likelihood)."""
    headers = auth_headers(faculty_lead)
    # CRITICAL (weight 4) * HIGH (weight 3) = 12
    payload = {
        "title": "Seasonal Monsoon Cloud Cover",
        "description": "Persistent overcast conditions during July-August may reduce solar thermal yield below daily minimum targets.",
        "severity": "critical",
        "likelihood": "high",
        "mitigation_plan": "Incorporate auxiliary biomass pellet backup burner for continuous thermal operation during heavy rains.",
    }
    resp = client.post(f"/api/v1/projects/{active_project.id}/risks", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["severity"] == RiskSeverity.CRITICAL.value
    assert data["likelihood"] == RiskLikelihood.HIGH.value
    assert data["risk_score"] == 12
    assert data["status"] == RiskStatus.OPEN.value


def test_unauthorized_user_cannot_resolve_risk(client: TestClient, citizen_user, faculty_lead, active_project):
    """16. Unrelated user cannot resolve a project risk."""
    headers_fac = auth_headers(faculty_lead)
    resp_r = client.post(
        f"/api/v1/projects/{active_project.id}/risks",
        json={"title": "Alumina Supply Delay", "description": "Vendor delivery risk", "severity": "medium", "likelihood": "low"},
        headers=headers_fac,
    )
    risk_id = resp_r.json()["id"]

    headers_cit = auth_headers(citizen_user)
    resp_resolve = client.post(
        f"/api/v1/risks/{risk_id}/resolve",
        json={"resolution_notes": "Citizen trying to resolve"},
        headers=headers_cit,
    )
    assert resp_resolve.status_code == 403


def test_automatic_activity_recording(client: TestClient, faculty_lead, active_project, db_session):
    """17. Project actions automatically write activity timeline records."""
    headers = auth_headers(faculty_lead)

    # Create team
    client.post(f"/api/v1/projects/{active_project.id}/teams", json={"name": "Logistics Roster"}, headers=headers)

    # Create risk
    client.post(
        f"/api/v1/projects/{active_project.id}/risks",
        json={"title": "Transport Risk", "description": "Road accessibility", "severity": "low", "likelihood": "low"},
        headers=headers,
    )

    # Query activities
    activities = db_session.query(ProjectActivity).filter(ProjectActivity.project_id == active_project.id).all()
    types = [a.activity_type for a in activities]
    assert ProjectActivityType.TEAM_CREATED.value in types
    assert ProjectActivityType.RISK_CREATED.value in types


def test_authorized_stakeholder_can_retrieve_timeline(client: TestClient, faculty_lead, active_project):
    """18. Authorized user can retrieve paginated project timeline with metadata."""
    headers = auth_headers(faculty_lead)
    resp = client.get(f"/api/v1/projects/{active_project.id}/timeline?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "pagination" in data
    assert isinstance(data["data"], list)


def test_unauthorized_user_cannot_access_private_timeline(client: TestClient, active_project, db_session):
    """19. Non-participant citizen cannot view private project timeline."""
    unrelated_user = User(
        full_name="Stranger User",
        email=f"stranger.{uuid.uuid4().hex[:6]}@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(unrelated_user)
    db_session.commit()
    db_session.refresh(unrelated_user)
    headers_stranger = auth_headers(unrelated_user)

    resp = client.get(f"/api/v1/projects/{active_project.id}/timeline", headers=headers_stranger)
    assert resp.status_code == 403


def test_end_to_end_project_collaboration_lifecycle(
    client: TestClient,
    faculty_lead,
    student_user,
    govt_officer,
    industry_org,
    industry_admin,
    active_project,
    db_session,
):
    """
    20. Complete End-to-End Institutional Project Lifecycle:
    Project Provisioning
    -> Multidisciplinary Team Assembly
    -> Solution Proposal Submission & Nodal Approval
    -> Milestone Scheduling & Deliverable Review
    -> Industry CSR Sponsorship Onboarding & Support Commitment
    -> Risk Identification & Mitigation Resolution
    -> Timeline & Project Dashboard Verification
    """
    headers_fac = auth_headers(faculty_lead)
    headers_govt = auth_headers(govt_officer)
    headers_csr = auth_headers(industry_admin)

    # 1. Team Assembly
    resp_team = client.post(
        f"/api/v1/projects/{active_project.id}/teams",
        json={"name": "Integrated Solar Desalination Team", "description": "Faculty mentor, students, and research engineers"},
        headers=headers_fac,
    )
    assert resp_team.status_code == 201
    team_id = resp_team.json()["id"]

    # Add student member
    resp_mem = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": student_user.id, "role": "student"},
        headers=headers_fac,
    )
    assert resp_mem.status_code == 201

    # 2. Proposal Submission & Approval
    resp_prop = client.post(
        f"/api/v1/projects/{active_project.id}/proposals",
        json={
            "submitted_by_team_id": team_id,
            "title": "Comprehensive Solar Defluoridation System Proposal",
            "summary": "Engineering blueprint for automated community clean water station in Dhanbad.",
            "detailed_description": "Complete CAD diagrams, alumina bed sizing, photovoltaic circuit diagrams, and field deployment timeline.",
            "estimated_budget": "INR 5,00,000",
        },
        headers=headers_fac,
    )
    assert resp_prop.status_code == 201
    prop_id = resp_prop.json()["id"]

    # Submit proposal
    client.post(f"/api/v1/proposals/{prop_id}/submit", headers=headers_fac)

    # Government officer approves proposal
    resp_prop_app = client.post(
        f"/api/v1/proposals/{prop_id}/review",
        json={"decision": "approve", "review_comment": "Project blueprint thoroughly verified and approved for state funding."},
        headers=headers_govt,
    )
    assert resp_prop_app.status_code == 200
    assert resp_prop_app.json()["status"] == ProposalStatus.APPROVED.value

    # 3. Milestone & Deliverable
    resp_m = client.post(
        f"/api/v1/projects/{active_project.id}/milestones",
        json={
            "title": "Field Pilot Rig Assembly",
            "description": "Assemble physical 500L pilot rig at BIT Sindri renewable energy test site.",
            "sequence_number": 1,
            "completion_percentage": 100,
        },
        headers=headers_fac,
    )
    assert resp_m.status_code == 201
    milestone_id = resp_m.json()["id"]

    # Submit deliverable
    resp_del = client.post(
        f"/api/v1/milestones/{milestone_id}/deliverables",
        json={
            "title": "Rig Assembly Photographic Log and Flow Test Certification",
            "description": "Factory testing logs verifying continuous 500L/day water flow rate.",
        },
        headers=headers_fac,
    )
    assert resp_del.status_code == 201
    del_id = resp_del.json()["id"]

    # Review deliverable
    resp_del_rev = client.post(
        f"/api/v1/deliverables/{del_id}/review",
        json={"decision": "accept", "review_comment": "Flow verification test certified."},
        headers=headers_govt,
    )
    assert resp_del_rev.status_code == 200
    assert resp_del_rev.json()["status"] == DeliverableStatus.ACCEPTED.value

    # 4. Industry/CSR Partnership
    resp_partner = client.post(
        f"/api/v1/projects/{active_project.id}/partners/invite",
        json={
            "organization_id": industry_org.id,
            "partner_type": "csr",
            "invitation_message": "Formal invitation to co-fund Govindpur deployment.",
        },
        headers=headers_fac,
    )
    assert resp_partner.status_code == 201
    partner_id = resp_partner.json()["id"]

    # Partner accepts
    resp_acc = client.post(
        f"/api/v1/project-partners/{partner_id}/accept",
        json={"decision": "accept", "response_message": "Tata Steel CSR joins this initiative."},
        headers=headers_csr,
    )
    assert resp_acc.status_code == 200

    # Partner adds support commitment
    resp_sup = client.post(
        f"/api/v1/project-partners/{partner_id}/support",
        json={
            "support_type": "funding",
            "description": "Equipment Procurement Grant",
            "estimated_value": "INR 2,50,000",
        },
        headers=headers_csr,
    )
    assert resp_sup.status_code == 201

    # 5. Risk Management
    resp_risk = client.post(
        f"/api/v1/projects/{active_project.id}/risks",
        json={
            "title": "Extreme Summer Heat Effect on Solar Array Efficiency",
            "description": "Ambient temperatures > 44°C may reduce PV inverter conversion efficiency.",
            "severity": "medium",
            "likelihood": "high",
            "mitigation_plan": "Install passive evaporative cooling shrouds around inverter enclosure.",
        },
        headers=headers_fac,
    )
    assert resp_risk.status_code == 201
    risk_id = resp_risk.json()["id"]
    assert resp_risk.json()["risk_score"] == 6  # medium(2) * high(3) = 6

    # Resolve risk
    resp_risk_res = client.post(
        f"/api/v1/risks/{risk_id}/resolve",
        json={"resolution_notes": "Passive water jacket installed and temperature drop verified."},
        headers=headers_fac,
    )
    assert resp_risk_res.status_code == 200
    assert resp_risk_res.json()["status"] == RiskStatus.RESOLVED.value

    # 6. Final Project State Inspection
    resp_proj = client.get(f"/api/v1/projects/{active_project.id}", headers=headers_fac)
    assert resp_proj.status_code == 200
    proj_data = resp_proj.json()
    assert len(proj_data["teamMembers"]) >= 2
    assert len(proj_data["milestones"]) >= 1
    assert len(proj_data["risks"]) >= 1

    # 7. Timeline verification
    resp_time = client.get(f"/api/v1/projects/{active_project.id}/timeline", headers=headers_fac)
    assert resp_time.status_code == 200
    timeline_items = resp_time.json()["data"]
    assert len(timeline_items) >= 5
