import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

from app.models.user import User
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup in-memory engine
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

session = Session()

def override_db():
    try:
        yield session
    finally:
        pass

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

print("--- Step 16 Verification Script ---")

# 1. GET /
r = client.get("/")
assert r.status_code == 200, f"GET / failed: {r.text}"
print("[OK] GET /: 200 OK")

# 2. GET /api/v1/health
r = client.get("/api/v1/health")
assert r.status_code == 200, f"GET /api/v1/health failed: {r.text}"
print("[OK] GET /api/v1/health: 200 OK")

# 3. GET /api/v1/system/status
r = client.get("/api/v1/system/status")
assert r.status_code == 200, f"GET /api/v1/system/status failed: {r.text}"
print("[OK] GET /api/v1/system/status: 200 OK")

# 4. POST /api/v1/auth/register
reg_payload = {
    "full_name": "Dr. Ananya Sen",
    "email": "ananya.sen@example.com",
    "password": "StrongPassword123!",
}
r = client.post("/api/v1/auth/register", json=reg_payload)
assert r.status_code == 201, f"POST /api/v1/auth/register failed: {r.text}"
user_id = r.json()["id"]
print(f"[OK] POST /api/v1/auth/register: 201 Created (id={user_id})")

# 5. POST /api/v1/auth/login
login_payload = {
    "email": "ananya.sen@example.com",
    "password": "StrongPassword123!",
}
r = client.post("/api/v1/auth/login", json=login_payload)
assert r.status_code == 200, f"POST /api/v1/auth/login failed: {r.text}"
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] POST /api/v1/auth/login: 200 OK")

# 6. GET /api/v1/auth/me
r = client.get("/api/v1/auth/me", headers=headers)
assert r.status_code == 200, f"GET /api/v1/auth/me failed: {r.text}"
print(f"[OK] GET /api/v1/auth/me: 200 OK (email={r.json()['email']}, role={r.json()['role']})")

# 7. GET /api/v1/organizations (empty list initially)
r = client.get("/api/v1/organizations")
assert r.status_code == 200, f"GET /api/v1/organizations failed: {r.text}"
assert r.json()["pagination"]["total"] == 0
print("[OK] GET /api/v1/organizations: 200 OK (total=0)")

# 8. POST /api/v1/organizations
org_payload = {
    "name": "Ranchi Agro Innovation Foundation",
    "organization_type": "startup",
    "district": "Ranchi",
    "state": "Jharkhand",
    "description": "Smart agriculture solutions for tribal farmers in Ranchi district.",
}
r = client.post("/api/v1/organizations", json=org_payload, headers=headers)
assert r.status_code == 201, f"POST /api/v1/organizations failed: {r.text}"
org_data = r.json()
org_id = org_data["id"]
print(f"[OK] POST /api/v1/organizations: 201 Created (id={org_id}, name={org_data['name']})")

# 9. GET /api/v1/organizations/{org_id}
r = client.get(f"/api/v1/organizations/{org_id}")
assert r.status_code == 200, f"GET /api/v1/organizations/{org_id} failed: {r.text}"
assert r.json()["name"] == "Ranchi Agro Innovation Foundation"
print(f"[OK] GET /api/v1/organizations/{org_id}: 200 OK")

# 10. PATCH /api/v1/organizations/{org_id}
patch_payload = {
    "website": "https://ranchiagro.org",
    "description": "Updated mission: Advanced precision farming and drone technology.",
}
r = client.patch(f"/api/v1/organizations/{org_id}", json=patch_payload, headers=headers)
assert r.status_code == 200, f"PATCH /api/v1/organizations/{org_id} failed: {r.text}"
assert r.json()["website"] == "https://ranchiagro.org"
print(f"[OK] PATCH /api/v1/organizations/{org_id}: 200 OK")

# 11. GET /api/v1/organizations/{org_id}/members
r = client.get(f"/api/v1/organizations/{org_id}/members")
assert r.status_code == 200, f"GET /api/v1/organizations/{org_id}/members failed: {r.text}"
members = r.json()
assert len(members) == 1
assert members[0]["user_id"] == user_id
assert members[0]["membership_role"] == "owner"
print(f"[OK] GET /api/v1/organizations/{org_id}/members: 200 OK (count={len(members)}, role={members[0]['membership_role']})")

print("\n--- ALL VERIFICATIONS PASSED SUCCESSFULLY ---")

