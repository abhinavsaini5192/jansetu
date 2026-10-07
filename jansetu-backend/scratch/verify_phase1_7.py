"""
Manual Verification Script for Phase 1.7 — Challenge CRUD APIs.
Tests end-to-end HTTP calls against FastAPI TestClient with in-memory SQLite database.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# In-memory test engine
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

print("\n--- PHASE 1.7 END-TO-END VERIFICATION RUN ---")

# 1. System Health & Status
r = client.get("/")
assert r.status_code == 200, f"GET / failed: {r.text}"
print("[OK] GET /: 200 OK")

r = client.get("/api/v1/health")
assert r.status_code == 200, f"GET /api/v1/health failed: {r.text}"
print("[OK] GET /api/v1/health: 200 OK")

r = client.get("/api/v1/system/status")
assert r.status_code == 200, f"GET /api/v1/system/status failed: {r.text}"
print("[OK] GET /api/v1/system/status: 200 OK")

# 2. Register Citizen User
reg_payload = {
    "full_name": "Birsa Munda Representative",
    "email": "birsa.rep@example.com",
    "password": "Password123!",
}
r = client.post("/api/v1/auth/register", json=reg_payload)
assert r.status_code == 201, f"Registration failed: {r.text}"
user_id = r.json()["id"]
print(f"[OK] POST /api/v1/auth/register: 201 Created (id={user_id})")

# 3. Login
login_payload = {
    "email": "birsa.rep@example.com",
    "password": "Password123!",
}
r = client.post("/api/v1/auth/login", json=login_payload)
assert r.status_code == 200, f"Login failed: {r.text}"
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] POST /api/v1/auth/login: 200 OK")

# 4. Get Current User Profile
r = client.get("/api/v1/auth/me", headers=headers)
assert r.status_code == 200, f"GET /auth/me failed: {r.text}"
print(f"[OK] GET /api/v1/auth/me: 200 OK (email={r.json()['email']})")

# 5. POST /api/v1/challenges
challenge_payload = {
    "title": "Severe Water Table Depletion in Torpa",
    "description": "Over-extraction has lowered the groundwater table by 15 meters, leaving three village tube wells completely dry.",
    "location": {
        "district": "Khunti",
        "block": "Torpa",
        "panchayat": "Dormo",
    },
    "domain": "water",
    "urgency": "critical",
    "affected_population": "450 farming families",
    "estimated_beneficiaries": 2200,
}
r = client.post("/api/v1/challenges", json=challenge_payload, headers=headers)
assert r.status_code == 201, f"POST /challenges failed: {r.text}"
challenge_data = r.json()
challenge_id = challenge_data["id"]
ref_code = challenge_data["reference_code"]
print(f"[OK] POST /api/v1/challenges: 201 Created (id={challenge_id}, ref={ref_code}, status={challenge_data['status']})")

# 6. GET /api/v1/challenges (Public Listing)
r = client.get("/api/v1/challenges?district=Khunti&domain=water")
assert r.status_code == 200, f"GET /challenges failed: {r.text}"
list_data = r.json()
assert list_data["pagination"]["total"] == 1
assert list_data["items"][0]["id"] == challenge_id
print(f"[OK] GET /api/v1/challenges: 200 OK (total={list_data['pagination']['total']}, items={len(list_data['items'])})")

# 7. GET /api/v1/challenges/my-submissions
r = client.get("/api/v1/challenges/my-submissions", headers=headers)
assert r.status_code == 200, f"GET /challenges/my-submissions failed: {r.text}"
my_sub = r.json()
assert my_sub["pagination"]["total"] == 1
assert my_sub["items"][0]["submitted_by_user_id"] == user_id
print(f"[OK] GET /api/v1/challenges/my-submissions: 200 OK (my submissions count={my_sub['pagination']['total']})")

# 8. GET /api/v1/challenges/{id}
r = client.get(f"/api/v1/challenges/{challenge_id}")
assert r.status_code == 200, f"GET /challenges/{challenge_id} failed: {r.text}"
detail_data = r.json()
assert detail_data["title"] == challenge_payload["title"]
assert detail_data["location"]["block"] == "Torpa"
print(f"[OK] GET /api/v1/challenges/{challenge_id}: 200 OK (title='{detail_data['title'][:30]}...')")

# 9. PATCH /api/v1/challenges/{id}
patch_payload = {
    "title": "Updated: Critical Water Table Depletion in Torpa Block",
    "urgency": "critical",
}
r = client.patch(f"/api/v1/challenges/{challenge_id}", json=patch_payload, headers=headers)
assert r.status_code == 200, f"PATCH /challenges/{challenge_id} failed: {r.text}"
updated_data = r.json()
assert updated_data["title"] == patch_payload["title"]
print(f"[OK] PATCH /api/v1/challenges/{challenge_id}: 200 OK (updated title='{updated_data['title'][:30]}...')")

# 10. DELETE /api/v1/challenges/{id}
r = client.delete(f"/api/v1/challenges/{challenge_id}", headers=headers)
assert r.status_code == 200, f"DELETE /challenges/{challenge_id} failed: {r.text}"
assert r.json()["success"] is True
print(f"[OK] DELETE /api/v1/challenges/{challenge_id}: 200 OK")

# 11. Verify 404 after deletion
r = client.get(f"/api/v1/challenges/{challenge_id}")
assert r.status_code == 404, f"Expected 404 after delete, got {r.status_code}"
print(f"[OK] GET /api/v1/challenges/{challenge_id} after DELETE: 404 Not Found (confirmed)")

print("\n--- ALL PHASE 1.7 ENDPOINTS VERIFIED SUCCESSFULLY ---")
