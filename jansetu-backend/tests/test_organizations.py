"""
Phase 1.5 Organization and Membership Management Tests.
Validates institutional lifecycle, RBAC authorization, and data integrity constraints.
"""
import uuid
import pytest
from app.core.security import create_access_token, hash_password
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.utils.constants import JHARKHAND_DISTRICTS
from app.utils.enums import (
    OrganizationMembershipRole,
    OrganizationType,
    UserRole,
)


def create_test_user(db_session, email: str, role: UserRole = UserRole.CITIZEN, full_name: str = "Test User") -> User:
    """Helper to persist a test user directly in the session."""
    user = User(
        id=str(uuid.uuid4()),
        full_name=full_name,
        email=email.strip().lower(),
        password_hash=hash_password("Password123!"),
        role=role,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_header(user: User) -> dict:
    """Helper to construct Authorization bearer header for a user."""
    token = create_access_token(subject=user.id)
    return {"Authorization": f"Bearer {token}"}



# ========================================================
# 1. Model Structure Tests
# ========================================================

def test_organization_model_imports_and_structure():
    """1. Verify Organization and OrganizationMembership models import cleanly with expected columns."""
    from app.models import Organization, OrganizationMembership

    assert hasattr(Organization, "id")
    assert hasattr(Organization, "name")
    assert hasattr(Organization, "organization_type")
    assert hasattr(Organization, "district")
    assert hasattr(Organization, "state")
    assert hasattr(Organization, "is_active")
    assert hasattr(Organization, "memberships")

    assert hasattr(OrganizationMembership, "id")
    assert hasattr(OrganizationMembership, "user_id")
    assert hasattr(OrganizationMembership, "organization_id")
    assert hasattr(OrganizationMembership, "membership_role")
    assert hasattr(OrganizationMembership, "is_active")


# ========================================================
# 2. Organization Lifecycle Tests
# ========================================================

def test_organization_creation_by_citizen(client, db_session):
    """2. Citizen can create an NGO/Startup organization and automatically becomes OWNER."""
    user = create_test_user(db_session, "creator.citizen@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    payload = {
        "name": "Jharkhand Rural Tech Foundation",
        "legal_name": "Jharkhand Rural Tech Foundation Trust",
        "organization_type": "ngo",
        "description": "Fostering technology adoption in rural Jharkhand.",
        "email": "contact@ruraltech.org",
        "district": "Ranchi",
        "state": "Jharkhand",
    }

    response = client.post("/api/v1/organizations", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jharkhand Rural Tech Foundation"
    assert data["organization_type"] == "ngo"
    assert data["district"] == "Ranchi"
    assert data["is_active"] is True
    assert "id" in data

    # Verify membership was automatically created as OWNER
    members_res = client.get(f"/api/v1/organizations/{data['id']}/members")
    assert members_res.status_code == 200
    members = members_res.json()
    assert len(members) == 1
    assert members[0]["user_id"] == user.id
    assert members[0]["membership_role"] == "owner"
    assert members[0]["is_active"] is True


def test_organization_retrieval_works(client, db_session):
    """3. Organization details can be retrieved by primary ID."""
    user = create_test_user(db_session, "org.retrieval@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    create_res = client.post(
        "/api/v1/organizations",
        json={"name": "Koderma Agri Innovation", "organization_type": "startup", "district": "Koderma"},
        headers=headers,
    )
    org_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/organizations/{org_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == org_id
    assert data["name"] == "Koderma Agri Innovation"
    assert data["district"] == "Koderma"


def test_organization_retrieval_not_found(client):
    """4. Querying non-existent organization returns 404 RESOURCE_NOT_FOUND."""
    response = client.get("/api/v1/organizations/non-existent-uuid-12345")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_organization_update_by_owner(client, db_session):
    """5. Organization owner can update organization metadata."""
    user = create_test_user(db_session, "org.updater@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    create_res = client.post(
        "/api/v1/organizations",
        json={"name": "Dhanbad Clean Energy Hub", "organization_type": "startup", "district": "Dhanbad"},
        headers=headers,
    )
    org_id = create_res.json()["id"]

    update_payload = {
        "website": "https://dhanbadcleanenergy.org",
        "description": "Pioneering renewable energy transitions in coal regions.",
    }
    patch_res = client.patch(f"/api/v1/organizations/{org_id}", json=update_payload, headers=headers)
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["website"] == "https://dhanbadcleanenergy.org"
    assert updated_data["description"] == update_payload["description"]


def test_organization_listing_and_filtering(client, db_session):
    """6. Listing organizations supports pagination and filtering by district and type."""
    admin = create_test_user(db_session, "listing.admin@example.com", UserRole.PLATFORM_ADMIN)
    headers = auth_header(admin)

    client.post("/api/v1/organizations", json={"name": "Bokaro Steel Research", "organization_type": "research_lab", "district": "Bokaro"}, headers=headers)
    client.post("/api/v1/organizations", json={"name": "Bokaro Agro Co-op", "organization_type": "community", "district": "Bokaro"}, headers=headers)
    client.post("/api/v1/organizations", json={"name": "Ranchi Health Labs", "organization_type": "research_lab", "district": "Ranchi"}, headers=headers)

    # Filter by Bokaro district
    res_bokaro = client.get("/api/v1/organizations?district=Bokaro")
    assert res_bokaro.status_code == 200
    data_bokaro = res_bokaro.json()
    assert data_bokaro["pagination"]["total"] == 2
    assert all(item["district"] == "Bokaro" for item in data_bokaro["items"])

    # Filter by research_lab type
    res_labs = client.get("/api/v1/organizations?type=research_lab")
    assert res_labs.status_code == 200
    data_labs = res_labs.json()
    assert data_labs["pagination"]["total"] == 2
    assert all(item["organization_type"] == "research_lab" for item in data_labs["items"])


def test_invalid_organization_type_rejected(client, db_session):
    """7. Unknown organization type fails validation with 422."""
    user = create_test_user(db_session, "type.tester@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    response = client.post(
        "/api/v1/organizations",
        json={"name": "Invalid Type Org", "organization_type": "alien_corporation"},
        headers=headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_district_rejected(client, db_session):
    """8. Invalid district name outside the 24 official Jharkhand districts fails with 422."""
    user = create_test_user(db_session, "district.tester@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    response = client.post(
        "/api/v1/organizations",
        json={"name": "Patna Tech Center", "organization_type": "startup", "district": "Patna"},
        headers=headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_valid_district_canonicalized(client, db_session):
    """9. Valid district with irregular casing is normalized to canonical title casing."""
    user = create_test_user(db_session, "canonical.tester@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    response = client.post(
        "/api/v1/organizations",
        json={"name": "Latehar Forest Initiative", "organization_type": "ngo", "district": "  lAtEhAr  "},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["district"] == "Latehar"


def test_duplicate_organization_name_rejected(client, db_session):
    """10. Creating duplicate organization name fails with 409 Conflict."""
    user = create_test_user(db_session, "dup.org@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    payload = {"name": "Unique Green Org", "organization_type": "ngo"}
    res1 = client.post("/api/v1/organizations", json=payload, headers=headers)
    assert res1.status_code == 201

    # Case-insensitive duplicate check
    res2 = client.post("/api/v1/organizations", json={"name": "unique green org", "organization_type": "ngo"}, headers=headers)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"


def test_inactive_organization_toggle(client, db_session):
    """11. Organization active status can be toggled by owner."""
    user = create_test_user(db_session, "status.toggle@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    create_res = client.post(
        "/api/v1/organizations",
        json={"name": "Temporary Project Org", "organization_type": "community"},
        headers=headers,
    )
    org_id = create_res.json()["id"]

    patch_res = client.patch(f"/api/v1/organizations/{org_id}", json={"is_active": False}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_active"] is False


# ========================================================
# 3. Membership & Role Authorization Tests
# ========================================================

def test_membership_addition_and_listing(client, db_session):
    """12. Organization owner can add new members and view membership list."""
    owner = create_test_user(db_session, "org.owner1@example.com", UserRole.CITIZEN)
    member = create_test_user(db_session, "org.member1@example.com", UserRole.STUDENT, "Student Member")
    owner_headers = auth_header(owner)

    create_res = client.post(
        "/api/v1/organizations",
        json={"name": "Simdega Skills Network", "organization_type": "ngo"},
        headers=owner_headers,
    )
    org_id = create_res.json()["id"]

    add_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": member.id, "membership_role": "member"},
        headers=owner_headers,
    )
    assert add_res.status_code == 201
    data = add_res.json()
    assert data["user_id"] == member.id
    assert data["membership_role"] == "member"
    assert data["is_active"] is True

    # Check list
    list_res = client.get(f"/api/v1/organizations/{org_id}/members")
    assert list_res.status_code == 200
    members = list_res.json()
    assert len(members) == 2  # Owner + Member


def test_duplicate_membership_rejected(client, db_session):
    """13. Adding an existing active member returns 409 Conflict."""
    owner = create_test_user(db_session, "org.owner2@example.com", UserRole.CITIZEN)
    member = create_test_user(db_session, "org.member2@example.com", UserRole.RESEARCHER)
    owner_headers = auth_header(owner)

    create_res = client.post("/api/v1/organizations", json={"name": "Garhwa Innovation Hub", "organization_type": "startup"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    # First add
    client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": member.id, "membership_role": "member"}, headers=owner_headers)

    # Second duplicate add
    dup_res = client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": member.id, "membership_role": "member"}, headers=owner_headers)
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "CONFLICT"


def test_membership_role_update_and_deactivation(client, db_session):
    """14. Member role can be promoted to ADMIN and deactivated."""
    owner = create_test_user(db_session, "org.owner3@example.com", UserRole.CITIZEN)
    member = create_test_user(db_session, "org.member3@example.com", UserRole.FACULTY)
    owner_headers = auth_header(owner)

    create_res = client.post("/api/v1/organizations", json={"name": "Hazaribagh Agro Labs", "organization_type": "startup"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": member.id, "membership_role": "member"}, headers=owner_headers)

    # Promote to admin
    promote_res = client.patch(
        f"/api/v1/organizations/{org_id}/members/{member.id}",
        json={"membership_role": "admin"},
        headers=owner_headers,
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["membership_role"] == "admin"

    # Deactivate
    deact_res = client.patch(
        f"/api/v1/organizations/{org_id}/members/{member.id}",
        json={"is_active": False},
        headers=owner_headers,
    )
    assert deact_res.status_code == 200
    assert deact_res.json()["is_active"] is False


def test_unauthorized_member_management_rejected(client, db_session):
    """15. Regular member or outsider cannot add or remove members (403 Forbidden)."""
    owner = create_test_user(db_session, "org.owner4@example.com", UserRole.CITIZEN)
    regular_member = create_test_user(db_session, "org.member4@example.com", UserRole.CITIZEN)
    outsider = create_test_user(db_session, "org.outsider@example.com", UserRole.CITIZEN)
    new_user = create_test_user(db_session, "org.newuser@example.com", UserRole.CITIZEN)

    owner_headers = auth_header(owner)
    member_headers = auth_header(regular_member)
    outsider_headers = auth_header(outsider)

    create_res = client.post("/api/v1/organizations", json={"name": "Palamu Water Society", "organization_type": "community"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    # Add regular member
    client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": regular_member.id, "membership_role": "member"}, headers=owner_headers)

    # Regular member tries to add someone
    member_attempt = client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": new_user.id}, headers=member_headers)
    assert member_attempt.status_code == 403

    # Outsider tries to add someone
    outsider_attempt = client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": new_user.id}, headers=outsider_headers)
    assert outsider_attempt.status_code == 403


def test_organization_admin_can_manage_members(client, db_session):
    """16. Organization ADMIN (promoted member) can enroll new members."""
    owner = create_test_user(db_session, "org.owner5@example.com", UserRole.CITIZEN)
    admin_user = create_test_user(db_session, "org.adminuser@example.com", UserRole.CITIZEN)
    candidate = create_test_user(db_session, "org.candidate@example.com", UserRole.CITIZEN)

    owner_headers = auth_header(owner)
    admin_headers = auth_header(admin_user)

    create_res = client.post("/api/v1/organizations", json={"name": "Giridih Tech Trust", "organization_type": "ngo"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    # Enroll as admin
    client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": admin_user.id, "membership_role": "admin"}, headers=owner_headers)

    # Admin enrolls candidate
    admin_add_res = client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"user_id": candidate.id, "membership_role": "member"},
        headers=admin_headers,
    )
    assert admin_add_res.status_code == 201
    assert admin_add_res.json()["user_id"] == candidate.id


def test_platform_admin_can_manage_any_organization(client, db_session):
    """17. Global platform admin has administrative authority over all organizations."""
    citizen = create_test_user(db_session, "creator.alone@example.com", UserRole.CITIZEN)
    platform_admin = create_test_user(db_session, "super.admin@example.com", UserRole.PLATFORM_ADMIN)
    target = create_test_user(db_session, "target.user@example.com", UserRole.CITIZEN)

    citizen_headers = auth_header(citizen)
    padmin_headers = auth_header(platform_admin)

    create_res = client.post("/api/v1/organizations", json={"name": "Deoghar Heritage Group", "organization_type": "community"}, headers=citizen_headers)
    org_id = create_res.json()["id"]

    # Platform admin updates organization directly
    patch_res = client.patch(f"/api/v1/organizations/{org_id}", json={"description": "Updated by Platform Admin"}, headers=padmin_headers)
    assert patch_res.status_code == 200

    # Platform admin adds a member
    add_res = client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": target.id, "membership_role": "member"}, headers=padmin_headers)
    assert add_res.status_code == 201


def test_sole_owner_cannot_be_removed_or_demoted(client, db_session):
    """18. The sole active owner of an organization cannot be deleted or demoted."""
    owner = create_test_user(db_session, "sole.owner@example.com", UserRole.CITIZEN)
    owner_headers = auth_header(owner)

    create_res = client.post("/api/v1/organizations", json={"name": "Gumla Bamboo Cluster", "organization_type": "community"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    # Attempt to demote sole owner
    demote_res = client.patch(
        f"/api/v1/organizations/{org_id}/members/{owner.id}",
        json={"membership_role": "member"},
        headers=owner_headers,
    )
    assert demote_res.status_code == 400
    assert "Cannot demote or deactivate the sole owner" in demote_res.json()["message"]

    # Attempt to remove sole owner
    remove_res = client.delete(f"/api/v1/organizations/{org_id}/members/{owner.id}", headers=owner_headers)
    assert remove_res.status_code == 400
    assert "Cannot remove the sole owner" in remove_res.json()["message"]


def test_member_removal_works(client, db_session):
    """19. A non-owner member can be removed cleanly by an owner."""
    owner = create_test_user(db_session, "remove.owner@example.com", UserRole.CITIZEN)
    member = create_test_user(db_session, "remove.member@example.com", UserRole.CITIZEN)
    owner_headers = auth_header(owner)

    create_res = client.post("/api/v1/organizations", json={"name": "Khunti Artisans Network", "organization_type": "community"}, headers=owner_headers)
    org_id = create_res.json()["id"]

    client.post(f"/api/v1/organizations/{org_id}/members", json={"user_id": member.id, "membership_role": "member"}, headers=owner_headers)

    del_res = client.delete(f"/api/v1/organizations/{org_id}/members/{member.id}", headers=owner_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verify member is gone
    members_res = client.get(f"/api/v1/organizations/{org_id}/members")
    assert len(members_res.json()) == 1


# ========================================================
# 4. Security & Institutional Governance Tests
# ========================================================

def test_citizens_cannot_create_government_or_university_orgs(client, db_session):
    """20. Citizens cannot freely create Government or University organizations without authorization."""
    citizen = create_test_user(db_session, "unauth.citizen@example.com", UserRole.CITIZEN)
    headers = auth_header(citizen)

    # Attempt to create government org
    gov_res = client.post(
        "/api/v1/organizations",
        json={"name": "Jharkhand Department of Mines", "organization_type": "government", "district": "Ranchi"},
        headers=headers,
    )
    assert gov_res.status_code == 403
    assert gov_res.json()["success"] is False

    # Attempt to create university org
    univ_res = client.post(
        "/api/v1/organizations",
        json={"name": "Ranchi Central University", "organization_type": "university", "district": "Ranchi"},
        headers=headers,
    )
    assert univ_res.status_code == 403
    assert univ_res.json()["success"] is False


def test_government_officer_can_create_government_org(client, db_session):
    """21. Authorized Government Admin can create a Government organization."""
    gov_admin = create_test_user(db_session, "nodal.officer@jharkhand.gov.in", UserRole.GOVERNMENT_ADMIN)
    headers = auth_header(gov_admin)

    res = client.post(
        "/api/v1/organizations",
        json={
            "name": "Jharkhand State Water Resources Department",
            "organization_type": "government",
            "district": "Ranchi",
            "description": "State level water management authority.",
        },
        headers=headers,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Jharkhand State Water Resources Department"
    assert data["organization_type"] == "government"


def test_university_admin_can_create_university_org(client, db_session):
    """22. University Admin can create a University organization."""
    univ_admin = create_test_user(db_session, "vc@bitmesra.ac.in", UserRole.UNIVERSITY_ADMIN)
    headers = auth_header(univ_admin)

    res = client.post(
        "/api/v1/organizations",
        json={
            "name": "Birla Institute of Technology Mesra",
            "organization_type": "university",
            "district": "Ranchi",
        },
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["organization_type"] == "university"


def test_membership_role_does_not_override_user_platform_role(client, db_session):
    """23. Being an OWNER of an organization does not elevate the user's platform role."""
    user = create_test_user(db_session, "role.check@example.com", UserRole.CITIZEN)
    headers = auth_header(user)

    client.post("/api/v1/organizations", json={"name": "Lohardaga Bauxite Crafts", "organization_type": "community"}, headers=headers)

    # Calling /auth/me to verify user role
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "citizen"  # Remains citizen!


def test_organization_deletion_cascades_to_memberships_not_users(db_session):
    """24. Cascading integrity: deleting an organization deletes membership records but preserves users."""
    user = create_test_user(db_session, "cascade.user@example.com", UserRole.CITIZEN)
    org = Organization(
        name="Temporary Cascade Org",
        organization_type=OrganizationType.NGO,
        district="Ranchi",
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        membership_role=OrganizationMembershipRole.OWNER,
    )
    db_session.add(membership)
    db_session.commit()

    # Delete the organization
    db_session.delete(org)
    db_session.commit()

    # Verify user still exists in database
    persisted_user = db_session.get(User, user.id)
    assert persisted_user is not None

    # Verify membership row is deleted
    persisted_membership = db_session.get(OrganizationMembership, membership.id)
    assert persisted_membership is None
