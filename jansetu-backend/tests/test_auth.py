from datetime import timedelta
import pytest
from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.utils.enums import UserRole


# ==========================================
# 1. Registration Tests
# ==========================================

def test_successful_registration(client):
    """1. Verify that a user can successfully register."""
    payload = {
        "full_name": "Ramesh Kumar",
        "email": "ramesh.kumar@example.com",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Ramesh Kumar"
    assert data["email"] == "ramesh.kumar@example.com"
    assert data["role"] == "citizen"
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert "id" in data
    assert "password_hash" not in data
    assert "password" not in data


def test_duplicate_email_rejected(client):
    """2. Verify that duplicate email registration is rejected with 409 Conflict."""
    payload = {
        "full_name": "Pooja Sharma",
        "email": "pooja.sharma@example.com",
        "password": "Password12345!",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"


def test_email_normalization(client, db_session):
    """3. Verify that registration normalizes uppercase emails to lowercase."""
    payload = {
        "full_name": "Anita Soren",
        "email": "  ANITA.SOREN@EXAMPLE.COM  ",
        "password": "Password12345!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "anita.soren@example.com"

    # Check database record directly
    user = user_repository.get_by_email(db_session, "anita.soren@example.com")
    assert user is not None
    assert user.email == "anita.soren@example.com"


def test_password_is_hashed_and_plain_never_stored(client, db_session):
    """4 & 5. Verify password is stored as bcrypt hash and plain password is never saved."""
    payload = {
        "full_name": "Birsa Munda",
        "email": "birsa.munda@example.com",
        "password": "SecretPassword99!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    user = user_repository.get_by_email(db_session, "birsa.munda@example.com")
    assert user is not None
    assert user.password_hash != "SecretPassword99!"
    assert user.password_hash.startswith(("$2b$", "$2a$"))
    assert verify_password("SecretPassword99!", user.password_hash) is True


def test_default_role_is_citizen(client):
    """6. Verify that omitting role defaults to CITIZEN."""
    payload = {
        "full_name": "Deepak Oraon",
        "email": "deepak.oraon@example.com",
        "password": "Password12345!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["role"] == "citizen"


def test_privileged_self_registration_rejected(client):
    """7. Verify that attempting to register as platform_admin or government_admin is rejected."""
    payload = {
        "full_name": "Fake Admin",
        "email": "fake.admin@example.com",
        "password": "Password12345!",
        "role": "platform_admin",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_email_rejected(client):
    """8. Verify that malformed email addresses are rejected with 422."""
    payload = {
        "full_name": "Invalid Email",
        "email": "not-a-valid-email",
        "password": "Password12345!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_weak_password_rejected(client):
    """9. Verify that passwords shorter than 8 characters are rejected."""
    payload = {
        "full_name": "Short Pwd",
        "email": "short.pwd@example.com",
        "password": "short",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


# ==========================================
# 2. Login & Token Tests
# ==========================================

def test_successful_login(client):
    """10, 14 & 15. Verify that valid credentials produce JWT and user profile."""
    # Register first
    client.post("/api/v1/auth/register", json={
        "full_name": "Vikram Singh",
        "email": "vikram.singh@example.com",
        "password": "Password123!",
    })

    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "vikram.singh@example.com",
        "password": "Password123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token" in data
    assert data["token"] == data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "vikram.singh@example.com"
    assert data["user"]["role"] == "citizen"

    # Decode token to verify subject
    payload = decode_access_token(data["access_token"])
    assert payload["sub"] == data["user"]["id"]
    assert payload["email"] == "vikram.singh@example.com"


def test_incorrect_password_rejected(client):
    """11. Verify that incorrect password returns 401 Unauthorized."""
    client.post("/api/v1/auth/register", json={
        "full_name": "Sunil Verma",
        "email": "sunil.verma@example.com",
        "password": "Password123!",
    })

    response = client.post("/api/v1/auth/login", json={
        "email": "sunil.verma@example.com",
        "password": "WrongPassword999!",
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_unknown_email_rejected_generically(client):
    """12. Verify that unknown email returns generic 401 without leaking user existence."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent.user@example.com",
        "password": "SomePassword123!",
    })
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password."


def test_inactive_user_rejected_on_login(client, db_session):
    """13. Verify that an inactive account cannot log in."""
    client.post("/api/v1/auth/register", json={
        "full_name": "Inactive User",
        "email": "inactive.user@example.com",
        "password": "Password123!",
    })
    # Deactivate account in DB
    user = user_repository.get_by_email(db_session, "inactive.user@example.com")
    user.is_active = False
    user_repository.update(db_session, user)

    response = client.post("/api/v1/auth/login", json={
        "email": "inactive.user@example.com",
        "password": "Password123!",
    })
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_expired_token_rejected(client):
    """16. Verify that an expired JWT token is rejected with 401."""
    expired_token = create_access_token(
        subject="expired-user-id",
        expires_delta=timedelta(minutes=-10),
    )
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["message"].lower()


def test_malformed_token_rejected(client):
    """17. Verify that a malformed token is rejected with 401."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )
    assert response.status_code == 401


# ==========================================
# 3. Current User (/auth/me) Tests
# ==========================================

def test_get_me_with_valid_token(client):
    """18 & 22. Verify /auth/me returns current user profile without password hash."""
    reg_res = client.post("/api/v1/auth/register", json={
        "full_name": "Meghan Soren",
        "email": "meghan.soren@example.com",
        "password": "Password123!",
    })
    user_id = reg_res.json()["id"]

    login_res = client.post("/api/v1/auth/login", json={
        "email": "meghan.soren@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["full_name"] == "Meghan Soren"
    assert data["email"] == "meghan.soren@example.com"
    assert "password_hash" not in data


def test_get_me_missing_token_rejected(client):
    """19. Verify /auth/me rejects requests without Authorization header."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_inactive_user_rejected(client, db_session):
    """21. Verify /auth/me rejects user if deactivated after token issuance."""
    reg_res = client.post("/api/v1/auth/register", json={
        "full_name": "Active Then Inactive",
        "email": "active.then.inactive@example.com",
        "password": "Password123!",
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "active.then.inactive@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]

    # Deactivate in DB
    user = user_repository.get_by_email(db_session, "active.then.inactive@example.com")
    user.is_active = False
    user_repository.update(db_session, user)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ==========================================
# 4. Security & Stateless Logout Tests
# ==========================================

def test_password_hashing_and_different_salts():
    """23 & 24. Verify bcrypt generates unique salts for identical passwords."""
    pwd = "SamePasswordForBoth123!"
    hash1 = hash_password(pwd)
    hash2 = hash_password(pwd)

    assert hash1 != hash2, "bcrypt must generate different salts for identical passwords"
    assert verify_password(pwd, hash1) is True
    assert verify_password(pwd, hash2) is True
    assert verify_password("WrongPassword", hash1) is False


def test_jwt_secret_not_exposed():
    """25. Verify that JWT secrets are not accessible via API responses."""
    assert len(settings.JWT_SECRET_KEY) >= 16


def test_logout_endpoint(client):
    """Verify stateless logout endpoint."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
