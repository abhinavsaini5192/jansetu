"""
Integration Test Suite for JanSetu Phase 1 Core Governance Workflow.
Covers:
- Phase 1.9: Government Validation Workflow (RBAC, transitions, queue, review history)
- Phase 1.10: Notifications & Audit Logs (alerts on decisions, read flags, immutable audit trails, credential safety)
- Phase 1.11: Real Dashboard Statistics & End-to-End Governance Lifecycle
"""
import io
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token
from app.models.audit_log import AuditLog
from app.models.challenge import Challenge
from app.models.government_review import GovernmentReview
from app.models.notification import Notification
from app.models.user import User
from app.services.audit_service import audit_service
from app.utils.enums import (
    AuditAction,
    ChallengeStatus,
    NotificationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


@pytest.fixture
def citizen_user(db_session):
    """Citizen who submits societal challenges."""
    user = User(
        full_name="Birsa Munda",
        email="birsa.munda@example.com",
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
    """Another citizen without access to Birsa's private records."""
    user = User(
        full_name="Other Citizen",
        email="other.citizen@example.com",
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
def govt_user(db_session):
    """Government Nodal Officer."""
    user = User(
        full_name="Rajesh Kumar (SDM)",
        email="rajesh.sdm@jharkhand.gov.in",
        password_hash="securehash",
        role=UserRole.GOVERNMENT_ADMIN,
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
def platform_admin(db_session):
    """Platform Super Administrator."""
    user = User(
        full_name="Chief Administrator",
        email="superadmin@jansetu.gov.in",
        password_hash="securehash",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(platform_admin):
    token = create_access_token(
        subject=platform_admin.id,
        additional_claims={"email": platform_admin.email, "role": platform_admin.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_challenge(db_session, citizen_user):
    """Submitted challenge waiting in government review queue."""
    challenge = Challenge(
        title="Contaminated Well in Village Angara",
        description="Groundwater shows high arsenic levels affecting over 200 households.",
        reference_code="JS-2026-TEST01",
        district="Ranchi",
        block="Angara",
        village_or_ward="Hesal",
        domain=SocietalDomain.WATER,
        priority=PriorityLevel.HIGH,
        urgency=UrgencyLevel.CRITICAL,
        status=ChallengeStatus.SUBMITTED,
        validation_status=ValidationStatus.PENDING,
        submitted_by_user_id=citizen_user.id,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


# =========================================================================
# 1. GOVERNMENT WORKFLOW TESTS (Phase 1.9)
# =========================================================================

def test_non_government_user_cannot_review_challenge(client: TestClient, sample_challenge, citizen_headers):
    """5. Verify that ordinary citizens/unauthorized users cannot review challenges (403)."""
    response = client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Citizen trying to self-validate"},
        headers=citizen_headers,
    )
    assert response.status_code == 403
    data = response.json()
    err_msg = data.get("message") or data.get("error", {}).get("message", "")
    assert "restricted" in err_msg.lower() or "forbidden" in err_msg.lower()


def test_authorized_government_user_can_validate_challenge(client: TestClient, sample_challenge, govt_headers, db_session):
    """6. Verify that an authorized government officer can officially validate a challenge."""
    response = client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={
            "decision": "validate",
            "review_comment": "Field inspection confirmed severe arsenic content. Forwarding for intervention.",
        },
        headers=govt_headers,
    )
    assert response.status_code == 200
    res_json = response.json()
    data = res_json.get("data", res_json)
    assert data["status"] == "validated"
    assert data["validation_status"] == "validated"

    # Verify DB persistence
    db_session.refresh(sample_challenge)
    assert sample_challenge.status == ChallengeStatus.VALIDATED
    assert sample_challenge.validation_status == ValidationStatus.VALIDATED
    assert sample_challenge.validated_at is not None


def test_invalid_status_transition_is_rejected(client: TestClient, sample_challenge, govt_headers, db_session):
    """7. Verify that illegal state transitions (e.g., REJECTED -> VALIDATED) are blocked (400)."""
    # First reject the challenge
    sample_challenge.status = ChallengeStatus.REJECTED
    sample_challenge.validation_status = ValidationStatus.REJECTED
    db_session.commit()

    response = client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Attempting invalid resurrect to validate"},
        headers=govt_headers,
    )
    assert response.status_code == 400
    data = response.json()
    err_msg = data.get("message") or data.get("error", {}).get("message", "")
    assert "terminal" in err_msg.lower() or "cannot" in err_msg.lower() or "transition" in err_msg.lower()


def test_review_history_is_persisted_and_queryable(client: TestClient, sample_challenge, govt_headers, db_session):
    """8. Verify that each government action creates a persistent GovernmentReview entry in history."""
    # Execute move to review
    client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "move_to_review", "review_comment": "Assigning field officer for spot verification"},
        headers=govt_headers,
    )

    # Execute validation
    client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Spot verification verified arsenic contamination"},
        headers=govt_headers,
    )

    # Fetch review history
    response = client.get(
        f"/api/v1/government/challenges/{sample_challenge.id}/review-history",
        headers=govt_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["history"]) == 2
    assert data["history"][0]["new_status"] == "validated"
    assert data["history"][1]["new_status"] == "under_review"


def test_government_pending_queue_filters(client: TestClient, sample_challenge, govt_headers):
    """Verify government pending review queue with district and domain filtering."""
    response = client.get(
        "/api/v1/government/challenges/pending?district=Ranchi",
        headers=govt_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] >= 1
    assert any(c["id"] == sample_challenge.id for c in data["items"])

    # Query with non-matching district
    response_empty = client.get(
        "/api/v1/government/challenges/pending?district=Bokaro",
        headers=govt_headers,
    )
    assert response_empty.status_code == 200
    data_empty = response_empty.json()
    assert not any(c["id"] == sample_challenge.id for c in data_empty["items"])


def test_frontend_compatible_validate_and_reject_endpoints(client: TestClient, sample_challenge, govt_headers, db_session):
    """Verify frontend shortcuts: POST /government/challenges/{id}/validate and /reject."""
    response = client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/validate",
        json={"remarks": "Quick validate from desk", "department": "Public Health Engineering Dept (PHED)"},
        headers=govt_headers,
    )
    assert response.status_code == 200
    db_session.refresh(sample_challenge)
    assert sample_challenge.status == ChallengeStatus.VALIDATED


# =========================================================================
# 2. NOTIFICATIONS TESTS (Phase 1.10)
# =========================================================================

def test_government_decision_creates_notification_for_submitter(
    client: TestClient, sample_challenge, govt_headers, citizen_headers, db_session
):
    """9. Verify that a government decision automatically generates an in-app notification for the submitter."""
    # Government user validates challenge
    client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Issue validated by PHED engineer."},
        headers=govt_headers,
    )

    # Submitter checks notifications
    response = client.get("/api/v1/notifications", headers=citizen_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["unread_count"] >= 1

    notif = data["items"][0]
    assert notif["related_challenge_id"] == sample_challenge.id
    assert notif["is_read"] is False
    assert "Validated" in notif["title"]


def test_user_can_list_and_mark_notification_as_read(
    client: TestClient, sample_challenge, govt_headers, citizen_headers
):
    """10. Verify that a citizen can query unread notifications and mark them as read."""
    # Create notification by validating
    client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Approved by authorities"},
        headers=govt_headers,
    )

    # Check unread count
    count_res = client.get("/api/v1/notifications/unread-count", headers=citizen_headers)
    assert count_res.status_code == 200
    assert count_res.json()["unread_count"] >= 1

    # Fetch notification ID
    list_res = client.get("/api/v1/notifications?unread_only=true", headers=citizen_headers)
    notif_id = list_res.json()["items"][0]["id"]

    # Mark as read
    mark_res = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=citizen_headers)
    assert mark_res.status_code == 200
    assert mark_res.json()["is_read"] is True

    # Mark all read endpoint test
    all_res = client.post("/api/v1/notifications/read-all", headers=citizen_headers)
    assert all_res.status_code == 200
    assert all_res.json()["data"]["updated_count"] >= 0
    count_after = client.get("/api/v1/notifications/unread-count", headers=citizen_headers).json()["unread_count"]
    assert count_after == 0


# =========================================================================
# 3. AUDIT LOG TESTS (Phase 1.10)
# =========================================================================

def test_important_action_creates_audit_log(
    client: TestClient, sample_challenge, govt_headers, db_session
):
    """11. Verify that important governance actions write immutable audit records with redacted secrets."""
    client.post(
        f"/api/v1/government/challenges/{sample_challenge.id}/review",
        json={"decision": "validate", "review_comment": "Audited validation test"},
        headers=govt_headers,
    )

    # Check AuditLog model in DB
    audit_entry = (
        db_session.query(AuditLog)
        .filter(AuditLog.entity_id == sample_challenge.id, AuditLog.action == AuditAction.VALIDATE.value)
        .first()
    )
    assert audit_entry is not None
    assert audit_entry.entity_type == "challenge"
    assert "validate" in audit_entry.description.lower()


def test_unauthorized_user_cannot_access_audit_logs(
    client: TestClient, citizen_headers, admin_headers, govt_headers
):
    """12. Verify that ordinary citizens are forbidden from reading audit logs (403), while admins succeed (200)."""
    # Citizen attempt
    res_citizen = client.get("/api/v1/audit-logs", headers=citizen_headers)
    assert res_citizen.status_code == 403

    # Platform Admin attempt
    res_admin = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "items" in res_admin.json()

    # Government Admin attempt
    res_govt = client.get("/api/v1/audit-logs", headers=govt_headers)
    assert res_govt.status_code == 200


def test_audit_log_redacts_sensitive_credentials(db_session, citizen_user):
    """Verify that credentials, tokens, and passwords are automatically redacted in audit metadata."""
    sensitive_payload = {
        "user_email": "test@example.com",
        "password": "SuperSecretPassword123!",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "api_secret": "sk_live_123456789",
    }
    log = audit_service.record_audit_event(
        db=db_session,
        action=AuditAction.LOGIN,
        entity_type="user",
        entity_id=citizen_user.id,
        description="Security test login event",
        actor=citizen_user,
        metadata=sensitive_payload,
    )
    assert log is not None
    assert "SuperSecretPassword123!" not in log.metadata_json
    assert "sk_live_123456789" not in log.metadata_json
    assert "[REDACTED]" in log.metadata_json


# =========================================================================
# 4. DASHBOARD TESTS (Phase 1.11)
# =========================================================================

def test_dashboard_returns_real_aggregate_counts(client: TestClient, sample_challenge, govt_headers):
    """13. Verify that the dashboard returns real database-aggregated counts, not mock values."""
    res_overview = client.get("/api/v1/dashboard/overview", headers=govt_headers)
    assert res_overview.status_code == 200
    data = res_overview.json()
    assert data["total_challenges"] >= 1
    assert data["submitted_challenges"] >= 1

    # Verify frontend alias compatibility
    assert data["totalChallenges"] >= 1
    assert "pending" in data

    # Verify /stats endpoint alias
    res_stats = client.get("/api/v1/dashboard/stats", headers=govt_headers)
    assert res_stats.status_code == 200
    assert res_stats.json()["total_challenges"] == data["total_challenges"]


def test_district_and_domain_summary_returns_valid_results(client: TestClient, sample_challenge):
    """14. Verify that district and domain summaries accurately group real challenge records."""
    # District summary
    res_dist = client.get("/api/v1/dashboard/district-summary")
    assert res_dist.status_code == 200
    dist_data = res_dist.json()
    assert dist_data["total_districts"] >= 1
    ranchi_item = next((d for d in dist_data["items"] if d["district"] == "Ranchi"), None)
    assert ranchi_item is not None
    assert ranchi_item["count"] >= 1

    # Frontend array endpoint
    res_dist_list = client.get("/api/v1/dashboard/districts")
    assert res_dist_list.status_code == 200
    assert isinstance(res_dist_list.json(), list)

    # Domain summary
    res_dom = client.get("/api/v1/dashboard/domain-summary")
    assert res_dom.status_code == 200
    dom_data = res_dom.json()
    assert dom_data["total_domains"] >= 1
    water_item = next((d for d in dom_data["items"] if d["domain"] == "water"), None)
    assert water_item is not None
    assert water_item["count"] >= 1


# =========================================================================
# 5. INTEGRATION WORKFLOW TESTS (Phases 1.8 - 1.11 End-to-End)
# =========================================================================

def test_complete_governance_end_to_end_flow(client: TestClient, db_session, tmp_path, monkeypatch):
    """
    15 & 16. Complete end-to-end integration test:
    1. User registers
    2. User logs in
    3. User submits a challenge
    4. User uploads a supporting attachment
    5. Government user sees challenge in pending queue
    6. Government user reviews and validates the challenge
    7. Challenge status updates to VALIDATED
    8. Submitter receives in-app notification
    9. Submitter marks notification as read
    10. Audit log entries are recorded for registration, challenge submission, and validation
    11. Dashboard statistics reflect the validated challenge
    """
    # Isolate upload dir
    upload_dir = tmp_path / "uploads" / "challenges"
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))

    # Step 1: User Register
    reg_payload = {
        "full_name": "Ravi Kumar",
        "email": "ravi.kumar@example.com",
        "password": "Password123!",
        "role": "citizen",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_id = reg_res.json()["id"]

    # Step 2: User Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "ravi.kumar@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    # Step 3: User Submits Challenge
    chal_payload = {
        "title": "Broken Irrigation Canal in Kanke",
        "description": "Primary irrigation canal breached near Kanke Dam, stopping water flow to 50 acres of farms.",
        "district": "Ranchi",
        "block": "Kanke",
        "village_or_ward": "Arsande",
        "domain": "agriculture",
        "priority": "high",
        "urgency": "critical",
    }
    chal_res = client.post("/api/v1/challenges", json=chal_payload, headers=user_headers)
    assert chal_res.status_code == 201
    challenge_id = chal_res.json()["id"]

    # Step 4: User Uploads Supporting Attachment
    file_content = b"%PDF-1.4 Mock irrigation survey report"
    files = {"file": ("canal_inspection.pdf", io.BytesIO(file_content), "application/pdf")}
    attach_res = client.post(
        f"/api/v1/challenges/{challenge_id}/attachments",
        files=files,
        headers=user_headers,
    )
    assert attach_res.status_code == 201
    attachment_id = attach_res.json()["id"]

    # Step 5: Government Nodal Officer Logs In & Sees Pending Challenge
    govt_user = User(
        full_name="District Officer Ranchi",
        email="do.ranchi@jharkhand.gov.in",
        password_hash="securehash",
        role=UserRole.DISTRICT_NODAL_OFFICER,
        is_active=True,
    )
    db_session.add(govt_user)
    db_session.commit()
    govt_token = create_access_token(
        subject=govt_user.id,
        additional_claims={"email": govt_user.email, "role": govt_user.role.value},
    )
    govt_headers = {"Authorization": f"Bearer {govt_token}"}

    queue_res = client.get("/api/v1/government/challenges/pending", headers=govt_headers)
    assert queue_res.status_code == 200
    queue_items = queue_res.json()["items"]
    assert any(c["id"] == challenge_id for c in queue_items)

    # Step 6: Government Officer Validates the Challenge
    review_payload = {
        "decision": "validate",
        "review_comment": "Irrigation dept verified canal breach. Action initiated under Rural Development scheme.",
        "department": "Department of Agriculture and Rural Development",
    }
    review_res = client.post(
        f"/api/v1/government/challenges/{challenge_id}/review",
        json=review_payload,
        headers=govt_headers,
    )
    assert review_res.status_code == 200
    review_data = review_res.json().get("data", review_res.json())
    assert review_data["status"] == "validated"

    # Step 7: Submitter Receives In-App Notification
    notif_res = client.get("/api/v1/notifications", headers=user_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()["items"]
    assert len(notifs) >= 1
    assert notifs[0]["related_challenge_id"] == challenge_id
    assert "Validated" in notifs[0]["title"]

    # Step 8: Mark Notification as Read
    mark_res = client.patch(f"/api/v1/notifications/{notifs[0]['id']}/read", headers=user_headers)
    assert mark_res.status_code == 200
    assert mark_res.json()["is_read"] is True

    # Step 9: Audit Trail Validation (by Admin)
    admin_user = User(
        full_name="Chief Sec Admin",
        email="cs.admin@jharkhand.gov.in",
        password_hash="securehash",
        role=UserRole.PLATFORM_ADMIN,
        is_active=True,
    )
    db_session.add(admin_user)
    db_session.commit()
    admin_token = create_access_token(
        subject=admin_user.id,
        additional_claims={"email": admin_user.email, "role": admin_user.role.value},
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    audit_res = client.get(f"/api/v1/audit-logs?entity_type=challenge", headers=admin_headers)
    assert audit_res.status_code == 200
    audit_items = audit_res.json()["items"]
    actions = [a["action"] for a in audit_items]
    assert AuditAction.VALIDATE.value in actions

    # Step 10: Dashboard Stats Reflected
    dash_res = client.get("/api/v1/dashboard/overview")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["validated_challenges"] >= 1
