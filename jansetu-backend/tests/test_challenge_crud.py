"""
Test suite for Phase 1.7 — Challenge CRUD APIs.
Verifies endpoints:
- POST   /api/v1/challenges
- GET    /api/v1/challenges
- GET    /api/v1/challenges/my-submissions
- GET    /api/v1/challenges/{id}
- PATCH  /api/v1/challenges/{id}
- DELETE /api/v1/challenges/{id}
"""
import pytest
from app.core.security import create_access_token
from app.models.challenge import Challenge
from app.models.user import User
from app.utils.enums import ChallengeStatus, SocietalDomain, UserRole, ValidationStatus


@pytest.fixture
def test_user(db_session):
    """Creates a verified citizen user for challenge submission."""
    user = User(
        full_name="Babulal Marandi",
        email="babulal.marandi@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Generates authorization headers for the primary test user."""
    token = create_access_token(
        subject=test_user.id,
        additional_claims={"email": test_user.email, "role": test_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db_session):
    """Creates a second distinct user for authorization boundary testing."""
    user = User(
        full_name="Priya Minz",
        email="priya.minz@example.com",
        password_hash="hashedpass",
        role=UserRole.CITIZEN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_auth_headers(second_user):
    """Generates authorization headers for the second test user."""
    token = create_access_token(
        subject=second_user.id,
        additional_claims={"email": second_user.email, "role": second_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# 1. Challenge Creation Tests
# ============================================================================

def test_authenticated_user_can_create_challenge(client, auth_headers, test_user):
    """1. Authenticated user can submit a societal challenge."""
    payload = {
        "title": "Severe arsenic contamination in Tube Well 4",
        "description": "Groundwater samples test 3x over permissible arsenic limits in Ramgarh town.",
        "district": "Ramgarh",
        "block": "Mandu",
        "domain": "water",
        "urgency": "critical",
        "affected_population": "800 residents",
        "estimated_beneficiaries": 800,
    }
    response = client.post("/api/v1/challenges", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["reference_code"].startswith("JS-")
    assert data["title"] == payload["title"]
    assert data["district"] == "Ramgarh"
    assert data["location"]["district"] == "Ramgarh"
    assert data["location"]["block"] == "Mandu"
    assert data["domain"] == "water"
    assert data["status"] == "submitted"
    assert data["validation_status"] == "pending"
    assert data["submitted_by_user_id"] == test_user.id
    assert data["submitted_by"] == test_user.full_name


def test_unauthenticated_user_cannot_create_challenge(client):
    """2. Unauthenticated user cannot create a challenge (401)."""
    payload = {
        "title": "Unauthorized Submission Test",
        "description": "Trying to submit a challenge without authentication token.",
        "district": "Ranchi",
        "domain": "agriculture",
    }
    response = client.post("/api/v1/challenges", json=payload)
    assert response.status_code == 401


def test_submitter_id_always_comes_from_authentication(client, auth_headers, test_user, second_user):
    """3 & 4. Client cannot override submitted_by_user_id (rejected by Pydantic schema or overridden)."""
    payload = {
        "title": "Impersonation Attempt In Challenge Creation",
        "description": "Submitting a challenge trying to attribute it to another citizen.",
        "district": "Ranchi",
        "domain": "agriculture",
        "submitted_by_user_id": second_user.id,
    }
    # Schema validation must reject client attempt to set system fields
    response = client.post("/api/v1/challenges", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "system-managed" in response.text


def test_default_statuses_are_submitted_and_pending(client, auth_headers):
    """5 & 6. Newly created challenge always has default status SUBMITTED and validation_status PENDING."""
    payload = {
        "title": "Broken Culvert on Rural Link Road",
        "description": "A collapsed culvert isolates 3 hamlets from primary healthcare access.",
        "district": "Khunti",
        "domain": "infrastructure",
    }
    response = client.post("/api/v1/challenges", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "submitted"
    assert data["validation_status"] == "pending"


def test_invalid_payload_rejected_with_422(client, auth_headers):
    """7. Invalid payload (e.g. invalid district or short description) is rejected with 422."""
    payload = {
        "title": "Short",
        "description": "Tiny",
        "district": "InvalidNonExistentDistrict",
        "domain": "water",
    }
    response = client.post("/api/v1/challenges", json=payload, headers=auth_headers)
    assert response.status_code == 422


# ============================================================================
# 2. Challenge Listing & Filtering Tests
# ============================================================================

def test_list_challenges_public_access_and_pagination(client, auth_headers):
    """8 & 9. Public challenge listing works and respects pagination limits."""
    # Seed 3 challenges
    for i in range(3):
        client.post(
            "/api/v1/challenges",
            json={
                "title": f"Community Problem Report #{i+1}",
                "description": f"Detailed description for test problem item #{i+1} in Bokaro district.",
                "district": "Bokaro",
                "domain": "education",
            },
            headers=auth_headers,
        )

    # Public GET (without headers)
    response = client.get("/api/v1/challenges?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["items"]) <= 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert data["pagination"]["total"] >= 3
    assert data["pagination"]["total_pages"] >= 2


def test_district_and_domain_filtering(client, auth_headers):
    """10 & 11. Challenge listing correctly filters by district and domain."""
    client.post(
        "/api/v1/challenges",
        json={
            "title": "Specific Ranchi Healthcare Issue",
            "description": "Primary healthcare center lacks refrigeration for vital vaccines.",
            "district": "Ranchi",
            "domain": "healthcare",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/challenges",
        json={
            "title": "Specific Dumka Agriculture Issue",
            "description": "Severe pest outbreak destroying seasonal pulses harvest.",
            "district": "Dumka",
            "domain": "agriculture",
        },
        headers=auth_headers,
    )

    # Filter by Ranchi
    res_ranchi = client.get("/api/v1/challenges?district=Ranchi")
    assert res_ranchi.status_code == 200
    items_ranchi = res_ranchi.json()["items"]
    assert all(c["district"] == "Ranchi" for c in items_ranchi)

    # Filter by domain agriculture
    res_agri = client.get("/api/v1/challenges?domain=agriculture")
    assert res_agri.status_code == 200
    items_agri = res_agri.json()["items"]
    assert all(c["domain"] == "agriculture" for c in items_agri)


def test_status_filtering_and_search(client, auth_headers):
    """12 & 13. Filtering by status and keyword search across title/description works."""
    client.post(
        "/api/v1/challenges",
        json={
            "title": "Solar Lighting Deficit in Simdega",
            "description": "Tribal hamlet in Simdega requires standalone micro-grid solutions.",
            "district": "Simdega",
            "domain": "energy",
        },
        headers=auth_headers,
    )

    # Search for "Simdega"
    res_search = client.get("/api/v1/challenges?search=Simdega")
    assert res_search.status_code == 200
    items = res_search.json()["items"]
    assert len(items) >= 1
    assert any("Simdega" in c["title"] or "Simdega" in c["district"] for c in items)

    # Status filter
    res_status = client.get("/api/v1/challenges?status=submitted")
    assert res_status.status_code == 200
    assert all(c["status"] == "submitted" for c in res_status.json()["items"])


def test_empty_results_handled_gracefully(client):
    """14. Unmatched filters return an empty list with total=0 without error."""
    response = client.get("/api/v1/challenges?search=NonExistentKeywordXYZ987")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["total_pages"] == 0


# ============================================================================
# 3. Challenge Details Tests
# ============================================================================

def test_get_challenge_detail_success_and_not_found(client, auth_headers):
    """15 & 16. Existing challenge detail can be fetched by ID; non-existent returns 404."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Bridge Railing Missing on River Ghat",
            "description": "Pedestrian safety hazard for schoolchildren crossing during monsoons.",
            "district": "Garhwa",
            "domain": "infrastructure",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    # 1. Fetch valid challenge
    get_res = client.get(f"/api/v1/challenges/{challenge_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == challenge_id
    assert data["district"] == "Garhwa"
    assert data["location"]["district"] == "Garhwa"

    # 2. Fetch missing challenge
    missing_res = client.get("/api/v1/challenges/non-existent-challenge-uuid")
    assert missing_res.status_code == 404
    assert "not found" in missing_res.text.lower()


# ============================================================================
# 4. Challenge Update & Ownership Tests
# ============================================================================

def test_owner_can_update_challenge_partially(client, auth_headers):
    """18 & 22. Submitter can update their challenge fields partially."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Initial Title for Waste Disposal Issue",
            "description": "Initial description of unauthorized chemical waste dumping.",
            "district": "Dhanbad",
            "domain": "sanitation",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    update_payload = {
        "title": "Updated Title: Hazardous Slag Dumping in Dhanbad",
        "urgency": "critical",
    }
    patch_res = client.patch(f"/api/v1/challenges/{challenge_id}", json=update_payload, headers=auth_headers)
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["title"] == update_payload["title"]
    assert updated_data["urgency"] == "critical"
    # Preserves unchanged description
    assert "chemical waste dumping" in updated_data["description"]


def test_non_owner_cannot_update_challenge(client, auth_headers, second_auth_headers):
    """19. User cannot update a challenge submitted by someone else (403)."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "User 1 Challenge For Ownership Boundary Check",
            "description": "Original challenge submitted by User 1.",
            "district": "Ranchi",
            "domain": "education",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    # User 2 tries to update User 1's challenge
    patch_res = client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"title": "Hacked Title Attempt"},
        headers=second_auth_headers,
    )
    assert patch_res.status_code == 403
    assert "permission" in patch_res.text.lower()


def test_locked_challenge_cannot_be_updated(client, auth_headers, db_session):
    """20. Challenge officially validated or rejected cannot be modified by submitter (403)."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Forest Fire Buffer Zone Initiative",
            "description": "Tribal community requests clearing fire buffers in dry season.",
            "district": "Latehar",
            "domain": "environment",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    # Directly simulate official review lock in DB (Phase 1.7 submitter lockdown)
    challenge = db_session.get(Challenge, challenge_id)
    challenge.status = ChallengeStatus.VALIDATED
    challenge.validation_status = ValidationStatus.VALIDATED
    db_session.commit()

    patch_res = client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"title": "Modified After Validation"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 403
    assert "locked" in patch_res.text.lower()


def test_client_cannot_change_system_fields_on_update(client, auth_headers):
    """21. Client cannot inject status or validation_status in update payload."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "System Field Lock Test Challenge",
            "description": "Testing that status cannot be updated via client payload.",
            "district": "Ranchi",
            "domain": "governance",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"status": "validated"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 422
    assert "system-managed" in patch_res.text


# ============================================================================
# 5. Challenge Deletion Tests
# ============================================================================

def test_owner_can_delete_challenge(client, auth_headers):
    """23. Submitter can delete their challenge before official review begins."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Accidental Duplicate Submission to be Deleted",
            "description": "User created this by mistake and chooses to delete it immediately.",
            "district": "Pakur",
            "domain": "agriculture",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/challenges/{challenge_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm it is now 404
    get_res = client.get(f"/api/v1/challenges/{challenge_id}")
    assert get_res.status_code == 404


def test_non_owner_cannot_delete_challenge(client, auth_headers, second_auth_headers):
    """24. User cannot delete another user's challenge (403)."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Challenge Protected from Unauthorized Deletion",
            "description": "Only the original author can delete this challenge.",
            "district": "Ranchi",
            "domain": "water",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/challenges/{challenge_id}", headers=second_auth_headers)
    assert del_res.status_code == 403


def test_locked_challenge_cannot_be_deleted(client, auth_headers, db_session):
    """25. Challenge in review or validated state cannot be deleted (403)."""
    create_res = client.post(
        "/api/v1/challenges",
        json={
            "title": "Active Review Underway For Canal Repair",
            "description": "Nodal team has already started site verification.",
            "district": "Palamu",
            "domain": "water",
        },
        headers=auth_headers,
    )
    challenge_id = create_res.json()["id"]

    challenge = db_session.get(Challenge, challenge_id)
    challenge.status = ChallengeStatus.UNDER_REVIEW
    db_session.commit()

    del_res = client.delete(f"/api/v1/challenges/{challenge_id}", headers=auth_headers)
    assert del_res.status_code == 403
    assert "review state" in del_res.text.lower()


# ============================================================================
# 6. My Submissions Isolation Tests
# ============================================================================

def test_my_submissions_returns_only_current_user_records(client, auth_headers, second_auth_headers, test_user, second_user):
    """26, 27, 28. /my-submissions returns only the authenticated user's records with pagination."""
    # User 1 submits 2 challenges
    for i in range(2):
        client.post(
            "/api/v1/challenges",
            json={
                "title": f"User 1 Submission #{i+1}",
                "description": f"Description for user 1 challenge #{i+1}.",
                "district": "Ranchi",
                "domain": "education",
            },
            headers=auth_headers,
        )

    # User 2 submits 1 challenge
    client.post(
        "/api/v1/challenges",
        json={
            "title": "User 2 Single Submission",
            "description": "Description for user 2 challenge.",
            "district": "Bokaro",
            "domain": "healthcare",
        },
        headers=second_auth_headers,
    )

    # Check User 1 submissions
    res1 = client.get("/api/v1/challenges/my-submissions", headers=auth_headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["pagination"]["total"] == 2
    assert all(c["submitted_by_user_id"] == test_user.id for c in data1["items"])
    assert all("User 1" in c["title"] for c in data1["items"])

    # Check User 2 submissions
    res2 = client.get("/api/v1/challenges/my-submissions", headers=second_auth_headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["pagination"]["total"] == 1
    assert data2["items"][0]["submitted_by_user_id"] == second_user.id
    assert data2["items"][0]["title"] == "User 2 Single Submission"
