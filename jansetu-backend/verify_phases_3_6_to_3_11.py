"""
Verification Script for JanSetu Backend Phases 3.6 to 3.11.
Verifies:
1. Backend vitality and health endpoints (GET /, /health, /api/v1/health, /api/v1/system/status).
2. Registration security (blocking privileged role self-assignment).
3. Project Workspace, Impact creation (Phase 3.6).
4. Evidence record attachment (Phase 3.7).
5. Government verification of impact (attestation & status change).
6. Real SQL Analytics (Phase 3.8: overview, challenges, projects, impact, districts, domains).
7. AI Project Intelligence with deterministic fallback (Phase 3.9).
8. Security / Auth checks (inactive user rejection, unauthorized user access rejection).
"""
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.challenge import Challenge
from app.models.impact_record import ImpactRecord
from app.models.evidence_record import EvidenceRecord
from app.models.milestone import Milestone
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_partner import ProjectPartner
from app.models.project_risk import ProjectRisk
from app.models.proposal import Proposal
from app.models.user import User
from app.utils.enums import (
    ChallengeStatus,
    ImpactStatus,
    ImpactType,
    InstitutionCategory,
    MilestoneStatus,
    OrganizationType,
    PartnerStatus,
    PartnerType,
    PriorityLevel,
    ProjectStatus,
    ProposalStatus,
    RiskSeverity,
    RiskStatus,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


def run_verification():
    print("==================================================")
    print("JANSETU PHASES 3.6 - 3.11 VERIFICATION RUN")
    print("==================================================")

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSession()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # -------------------------------------------------------------
    # 1. Health and Readiness Endpoints
    # -------------------------------------------------------------
    print("\n--- 1. Testing Health & Readiness Endpoints ---")
    r = client.get("/")
    assert r.status_code == 200, f"Root / failed: {r.text}"
    print("[PASS] GET / -> 200 OK")

    r = client.get("/health")
    assert r.status_code == 200, f"/health failed: {r.text}"
    assert r.json()["status"] == "healthy"
    print("[PASS] GET /health -> 200 OK (status=healthy)")

    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"/api/v1/health failed: {r.text}"
    print("[PASS] GET /api/v1/health -> 200 OK")

    r = client.get("/api/v1/system/status")
    assert r.status_code == 200, f"/api/v1/system/status failed: {r.text}"
    sys_data = r.json()["data"]
    assert "database" in sys_data
    assert "ai" in sys_data
    assert sys_data["ai"]["fallback_enabled"] is True
    print(f"[PASS] GET /api/v1/system/status -> 200 OK (DB={sys_data['database']['status']}, AI Provider={sys_data['ai']['provider']})")

    # -------------------------------------------------------------
    # 2. Authentication & Security Hardening
    # -------------------------------------------------------------
    print("\n--- 2. Testing Security & Privilege Escalation Hardening ---")
    # Attempt privileged self-assignment
    malicious_payload = {
        "full_name": "Hacker Admin",
        "email": "hacker@domain.gov",
        "password": "SecurePassword123!",
        "role": "platform_admin",
    }
    r = client.post("/api/v1/auth/register", json=malicious_payload)
    assert r.status_code in (400, 403, 422), f"Privilege self-assignment was not blocked: {r.status_code} {r.text}"
    print(f"[PASS] Blocked self-assignment of PLATFORM_ADMIN role ({r.status_code} Validation Rejection)")

    # -------------------------------------------------------------
    # Setup Test Users & Organizations in DB
    # -------------------------------------------------------------
    citizen = User(
        id=str(uuid.uuid4()),
        full_name="Ramesh Patel",
        email="ramesh@citizen.in",
        password_hash=hash_password("CitizenPass123!"),
        role=UserRole.CITIZEN,
        is_active=True,
    )
    gov_officer = User(
        id=str(uuid.uuid4()),
        full_name="Dr. V. Sharma (Nodal Officer)",
        email="v.sharma@gov.in",
        password_hash=hash_password("GovPass123!"),
        role=UserRole.GOVERNMENT_ADMIN,
        is_active=True,
    )
    uni_faculty = User(
        id=str(uuid.uuid4()),
        full_name="Prof. Anita Rao",
        email="anita.rao@iitb.ac.in",
        password_hash=hash_password("UniPass123!"),
        role=UserRole.FACULTY,
        is_active=True,
    )
    inactive_user = User(
        id=str(uuid.uuid4()),
        full_name="Inactive User",
        email="inactive@user.in",
        password_hash=hash_password("Inactive123!"),
        role=UserRole.CITIZEN,
        is_active=False,
    )
    db.add_all([citizen, gov_officer, uni_faculty, inactive_user])

    # Organizations
    uni_org = Organization(
        id=str(uuid.uuid4()),
        name="IIT Bombay",
        organization_type=OrganizationType.UNIVERSITY,
        district="Mumbai Suburban",
        state="Maharashtra",
        is_active=True,
    )
    industry_org = Organization(
        id=str(uuid.uuid4()),
        name="Tata Steel Foundation",
        organization_type=OrganizationType.INDUSTRY,
        district="East Singhbhum",
        state="Jharkhand",
        is_active=True,
    )
    db.add_all([uni_org, industry_org])
    db.commit()

    # Login check for inactive user
    r = client.post("/api/v1/auth/login", json={"email": "inactive@user.in", "password": "Inactive123!"})
    assert r.status_code == 403, f"Inactive user was not blocked: {r.status_code}"
    print("[PASS] Inactive user blocked from login (403 Forbidden)")

    # Tokens
    gov_token = create_access_token(subject=gov_officer.id, additional_claims={"role": gov_officer.role.value})
    uni_token = create_access_token(subject=uni_faculty.id, additional_claims={"role": uni_faculty.role.value})
    cit_token = create_access_token(subject=citizen.id, additional_claims={"role": citizen.role.value})

    gov_headers = {"Authorization": f"Bearer {gov_token}"}
    uni_headers = {"Authorization": f"Bearer {uni_token}"}
    cit_headers = {"Authorization": f"Bearer {cit_token}"}

    # Setup Challenge and Project
    challenge = Challenge(
        id=str(uuid.uuid4()),
        title="Fluoride Water Filtration in Rural Nalgonda",
        description="Groundwater fluoride levels exceed 5mg/L causing dental and skeletal fluorosis across 14 panchayats.",
        domain=SocietalDomain.WATER,
        district="Nalgonda",
        priority=PriorityLevel.HIGH,
        urgency=UrgencyLevel.CRITICAL,
        status=ChallengeStatus.VALIDATED,
        validation_status=ValidationStatus.VALIDATED,
        submitted_by_user_id=citizen.id,
    )
    db.add(challenge)
    db.commit()

    project = Project(
        id=str(uuid.uuid4()),
        project_code="PRJ-NALG-2026",
        challenge_id=challenge.id,
        university_id=uni_org.id,
        title="Nano-Membrane Community Filtration Unit",
        description="Low-cost solar-assisted nanofiltration removing 99% of fluoride ions.",
        status=ProjectStatus.ACTIVE,
        created_by_user_id=uni_faculty.id,
    )
    db.add(project)
    db.commit()

    # Add milestone, partner, and risk
    milestone = Milestone(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Community Prototype Deployment",
        sequence_number=1,
        status=MilestoneStatus.IN_PROGRESS,
        completion_percentage=75,
        created_by_user_id=uni_faculty.id,
    )
    risk = ProjectRisk(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Monsoon Supply Chain Delay",
        description="Filter membrane transport disrupted by heavy rain.",
        severity=RiskSeverity.HIGH,
        status=RiskStatus.OPEN,
        risk_score=7,
        mitigation_plan="Pre-stock replacement cartridges in local cluster hub.",
    )
    partner = ProjectPartner(
        id=str(uuid.uuid4()),
        project_id=project.id,
        organization_id=industry_org.id,
        partner_type=PartnerType.INDUSTRY,
        invited_by_user_id=uni_faculty.id,
        status=PartnerStatus.ACCEPTED,
    )
    db.add_all([milestone, risk, partner])
    db.commit()

    # -------------------------------------------------------------
    # 3. Phase 3.6 — Impact Management APIs
    # -------------------------------------------------------------
    print("\n--- 3. Testing Phase 3.6: Impact Management APIs ---")
    impact_payload = {
        "title": "Clean Drinking Water Delivery in Nalgonda Cluster",
        "description": "Deployment of 3 nanofiltration community plants reducing fluoride from 5.4mg/L to 0.6mg/L.",
        "impact_type": "health",
        "target_population": "Rural agricultural families in Nalgonda",
        "actual_beneficiaries": "12,400 residents",
        "geographic_coverage": "3 Gram Panchayats, Nalgonda",
        "villages_covered": 14,
        "baseline_value": "5.4 mg/L Fluoride",
        "achieved_value": "0.6 mg/L Fluoride",
        "measurement_unit": "mg/L Fluoride",
        "outcome_summary": "Zero new dental fluorosis symptoms recorded in pilot cohort over 6 months.",
        "economic_benefit": "Estimated INR 18 Lakhs saved in annual healthcare expenses.",
    }

    # University creates impact record
    r = client.post(f"/api/v1/projects/{project.id}/impact", json=impact_payload, headers=uni_headers)
    assert r.status_code == 200, f"Create impact failed: {r.text}"
    impact_data = r.json()["data"]
    impact_id = impact_data["id"]
    assert impact_data["status"] == "submitted"
    assert impact_data["isGovernmentVerified"] is False
    print(f"[PASS] POST /api/v1/projects/{project.id}/impact -> Created impact (id={impact_id})")

    # Get impact by ID
    r = client.get(f"/api/v1/impact/{impact_id}", headers=uni_headers)
    assert r.status_code == 200
    print("[PASS] GET /api/v1/impact/{id} -> 200 OK")

    # Get impact by challenge ID (Frontend Screen 09 compatibility)
    r = client.get(f"/api/v1/challenges/{challenge.id}/impact")
    assert r.status_code == 200, f"Get impact by challenge failed: {r.text}"
    assert r.json()["data"]["id"] == impact_id
    print("[PASS] GET /api/v1/challenges/{challenge_id}/impact -> 200 OK (Screen 09 format verified)")

    # -------------------------------------------------------------
    # 4. Phase 3.7 — Evidence Submission & Verification
    # -------------------------------------------------------------
    print("\n--- 4. Testing Phase 3.7: Evidence Submission & Verification ---")
    evidence_payload = {
        "title": "NABL Lab Water Purity Certificate",
        "evidence_type": "report",
        "description": "Certified spectroscopic test showing 0.6 mg/L fluoride level.",
        "source_reference": "NABL-LAB-HYD-2026-8812",
    }
    r = client.post(f"/api/v1/impact/{impact_id}/evidence", json=evidence_payload, headers=uni_headers)
    assert r.status_code == 200, f"Add evidence failed: {r.text}"
    ev_data = r.json()["data"]
    evidence_id = ev_data["id"]
    assert ev_data["verification_status"] == "pending"
    print(f"[PASS] POST /api/v1/impact/{impact_id}/evidence -> Added evidence (id={evidence_id})")

    # Verify evidence (government officer)
    r = client.post(
        f"/api/v1/evidence/{evidence_id}/verify",
        json={"decision": "VERIFIED", "verification_notes": "Official seal verified against Telangana PHED registry."},
        headers=gov_headers,
    )
    assert r.status_code == 200, f"Verify evidence failed: {r.text}"
    assert r.json()["data"]["verification_status"] == "verified"
    print("[PASS] POST /api/v1/evidence/{evidence_id}/verify -> 200 OK (verified by Nodal Officer)")

    # Unauthorized user attempting to verify evidence
    r = client.post(
        f"/api/v1/evidence/{evidence_id}/verify",
        json={"decision": "VERIFIED"},
        headers=cit_headers,
    )
    assert r.status_code == 403, f"Unauthorized verification not rejected: {r.status_code}"
    print("[PASS] Unauthorized user blocked from verifying evidence (403 Forbidden)")

    # -------------------------------------------------------------
    # 5. Government Verification of Impact Record
    # -------------------------------------------------------------
    print("\n--- 5. Testing Government Impact Verification ---")
    # Submitter cannot self-verify
    r = client.post(
        f"/api/v1/impact/{impact_id}/verify",
        json={"decision": "VERIFIED", "signatoryNote": "Self sign"},
        headers=uni_headers,
    )
    assert r.status_code == 403, f"Submitter self-verification was not blocked: {r.status_code}"
    print("[PASS] Submitter blocked from self-verifying impact assessment (403 Forbidden)")

    # Government officer verifies impact
    r = client.post(
        f"/api/v1/impact/{impact_id}/verify",
        json={"decision": "VERIFIED", "signatoryNote": "Inspected by Nalgonda District Collectorate on-site."},
        headers=gov_headers,
    )
    assert r.status_code == 200, f"Gov verify failed: {r.text}"
    v_data = r.json()["data"]
    assert v_data["status"] == "verified"
    assert v_data["isGovernmentVerified"] is True
    print("[PASS] POST /api/v1/impact/{impact_id}/verify -> Officially Verified (status=verified)")

    # -------------------------------------------------------------
    # 6. Phase 3.8 — Database-Backed Analytics Endpoints
    # -------------------------------------------------------------
    print("\n--- 6. Testing Phase 3.8: Database-Backed Analytics ---")
    r = client.get("/api/v1/analytics/overview")
    assert r.status_code == 200, f"Analytics overview failed: {r.text}"
    overview = r.json()
    assert overview["total_challenges"] >= 1
    assert overview["validated_challenges"] >= 1
    assert overview["total_projects"] >= 1
    assert overview["total_universities"] >= 1
    assert overview["total_partners"] >= 1
    assert overview["total_impact_records"] >= 1
    assert overview["verified_impact_records"] >= 1
    print(f"[PASS] GET /api/v1/analytics/overview -> Real DB aggregates (Challenges={overview['total_challenges']}, Verified Impact={overview['verified_impact_records']})")

    r = client.get("/api/v1/analytics/challenges")
    assert r.status_code == 200
    c_analytics = r.json()
    assert "Nalgonda" in c_analytics["by_district"]
    print("[PASS] GET /api/v1/analytics/challenges -> Grouped by district, domain, priority, status")

    r = client.get("/api/v1/analytics/projects")
    assert r.status_code == 200
    p_analytics = r.json()
    assert p_analytics["total_milestones"] >= 1
    assert p_analytics["active_risks_count"] >= 1
    print(f"[PASS] GET /api/v1/analytics/projects -> 200 OK (Milestones={p_analytics['total_milestones']}, Risks={p_analytics['active_risks_count']})")

    r = client.get("/api/v1/analytics/impact")
    assert r.status_code == 200
    imp_analytics = r.json()
    assert imp_analytics["total_villages_covered"] >= 14
    assert imp_analytics["verified_percentage"] == 100.0
    print(f"[PASS] GET /api/v1/analytics/impact -> 200 OK (Villages={imp_analytics['total_villages_covered']}, Verified%={imp_analytics['verified_percentage']}%)")

    r = client.get("/api/v1/analytics/districts")
    assert r.status_code == 200
    dist_list = r.json()
    assert len(dist_list) >= 1
    assert any(d["district"] == "Nalgonda" for d in dist_list)
    print("[PASS] GET /api/v1/analytics/districts -> 200 OK (Nalgonda district verified)")

    r = client.get("/api/v1/analytics/domains")
    assert r.status_code == 200
    dom_list = r.json()
    assert len(dom_list) >= 1
    print(f"[PASS] GET /api/v1/analytics/domains -> 200 OK ({len(dom_list)} domains represented)")

    # -------------------------------------------------------------
    # 7. Phase 3.9 — AI Project Intelligence with Fallback
    # -------------------------------------------------------------
    print("\n--- 7. Testing Phase 3.9: AI Project Intelligence ---")
    r = client.get(f"/api/v1/ai/projects/{project.id}/intelligence", headers=uni_headers)
    assert r.status_code == 200, f"Project intelligence failed: {r.text}"
    intel = r.json()
    assert intel["project_id"] == project.id
    assert intel["fallback_used"] is True
    assert intel["current_status"] == "active"
    assert len(intel["open_risks"]) >= 1
    assert len(intel["recommended_next_actions"]) >= 1
    print(f"[PASS] GET /api/v1/ai/projects/{project.id}/intelligence -> 200 OK")
    print(f"       Provider: {intel['provider']} (fallback={intel['fallback_used']})")
    print(f"       Summary: {intel['project_summary'][:80]}...")
    print(f"       Actions: {intel['recommended_next_actions']}")

    print("\n==================================================")
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_verification()
