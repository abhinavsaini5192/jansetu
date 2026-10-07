"""
Focused Test Suite for Phase 1.8 — Challenge File Attachments.
Verifies:
1. Attachment model & migration import and schema validation
2. Unauthenticated upload is rejected (401)
3. Authenticated challenge owner can upload a valid file (201)
4. Invalid extension or oversized file is rejected (400 / 413)
5. Attachment listing works for authorized challenge owner (200)
6. Unauthorized user cannot download/access another user's attachment (403)
7. Attachment deletion removes record safely (200)
8. Physical file cleanup works and missing physical file is handled gracefully
"""
import io
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token
from app.models.attachment import Attachment
from app.models.challenge import Challenge
from app.models.user import User
from app.utils.enums import ChallengeStatus, SocietalDomain, UserRole, ValidationStatus


@pytest.fixture(autouse=True)
def temp_upload_dir(tmp_path, monkeypatch):
    """Isolates file upload storage to a temporary directory for each test."""
    upload_dir = tmp_path / "uploads" / "challenges"
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))
    return upload_dir


@pytest.fixture
def test_user(db_session):
    """Primary citizen user who owns the challenge."""
    user = User(
        full_name="Sunita Soren",
        email="sunita.soren@example.com",
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
    """Bearer auth headers for primary user."""
    token = create_access_token(
        subject=test_user.id,
        additional_claims={"email": test_user.email, "role": test_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db_session):
    """Secondary user to verify permission boundaries."""
    user = User(
        full_name="Rajesh Oraon",
        email="rajesh.oraon@example.com",
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
    """Bearer auth headers for secondary user."""
    token = create_access_token(
        subject=second_user.id,
        additional_claims={"email": second_user.email, "role": second_user.role.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_challenge(db_session, test_user):
    """Active challenge owned by primary test user."""
    challenge = Challenge(
        reference_code="JH-RNC-2026-ATT01",
        submitted_by_user_id=test_user.id,
        title="Contaminated drinking water in Namkum village",
        description="Borewell water shows heavy turbidity and metal contamination.",
        district="Ranchi",
        block="Namkum",
        village_or_ward="Rampur",
        domain=SocietalDomain.WATER,
        status=ChallengeStatus.SUBMITTED,
        validation_status=ValidationStatus.PENDING,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


# ---------------------------------------------------------------------------
# Test Cases (1 to 8)
# ---------------------------------------------------------------------------


def test_attachment_model_and_migration_imports():
    """1. Verify Attachment model and Alembic migration exist and have proper attributes."""
    assert hasattr(Attachment, "id")
    assert hasattr(Attachment, "challenge_id")
    assert hasattr(Attachment, "uploaded_by_user_id")
    assert hasattr(Attachment, "stored_filename")
    assert hasattr(Attachment, "storage_path")
    assert hasattr(Attachment, "mime_type")
    assert hasattr(Attachment, "file_size")
    assert hasattr(Attachment, "file_extension")
    assert hasattr(Attachment, "created_at")
    assert Attachment.__tablename__ == "attachments"

    # Verify migration 0005 exists
    alembic_dir = Path(__file__).resolve().parent.parent / "alembic" / "versions"
    migration_file = alembic_dir / "0005_create_attachments_table.py"
    assert migration_file.is_file(), "Migration 0005_create_attachments_table.py must exist"

    with open(migration_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert 'revision: str = "0005_attachments"' in content
    assert 'down_revision: Union[str, None] = "0004_challenges"' in content


def test_unauthenticated_upload_rejected(client: TestClient, test_challenge: Challenge):
    """2. Verify unauthenticated upload is rejected with 401 Unauthorized."""
    file_content = b"%PDF-1.4 Fake PDF Content"
    response = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        files={"file": ("report.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 401


def test_authenticated_challenge_owner_can_upload_valid_file(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
    temp_upload_dir: Path,
):
    """3. Verify authenticated challenge owner can upload a valid PDF file."""
    file_content = b"%PDF-1.4 Valid problem evidence document content."
    response = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("water_test_report.pdf", io.BytesIO(file_content), "application/pdf")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["challenge_id"] == test_challenge.id
    assert data["original_filename"] == "water_test_report.pdf"
    assert data["mime_type"] == "application/pdf"
    assert data["file_extension"] == ".pdf"
    assert data["file_size"] == len(file_content)
    assert "download_url" in data
    assert f"/api/v1/attachments/{data['id']}/download" in data["download_url"]

    # Verify internal server path is NOT exposed in the response
    assert "storage_path" not in data
    assert str(temp_upload_dir) not in str(data)

    # Verify physical file was written to upload dir
    files_on_disk = list(temp_upload_dir.glob("*.pdf"))
    assert len(files_on_disk) == 1
    assert files_on_disk[0].read_bytes() == file_content


def test_invalid_extension_or_oversized_file_rejected(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
    monkeypatch,
):
    """4. Verify prohibited file extensions and oversized files are rejected."""
    # Prohibited extension: .exe
    response_exe = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload")},
    )
    assert response_exe.status_code == 400
    assert "strictly prohibited" in response_exe.json()["message"]

    # Prohibited extension: .sh
    response_sh = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("script.sh", io.BytesIO(b"#!/bin/bash\nrm -rf /"), "text/x-shellscript")},
    )
    assert response_sh.status_code == 400

    # Oversized file: set max size to 1 MB for testing and upload 1.5 MB
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)
    large_content = b"0" * (1024 * 1024 + 100)  # > 1MB
    response_large = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("huge_doc.pdf", io.BytesIO(large_content), "application/pdf")},
    )
    assert response_large.status_code == 413


def test_attachment_listing_works_for_authorized_owner(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
):
    """5. Verify listing attachments works for authorized challenge owner."""
    # Upload first file
    client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("photo1.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    # Upload second file
    client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("document.docx", io.BytesIO(b"PK\x03\x04 fake docx"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    response = client.get(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    filenames = [item["original_filename"] for item in data["items"]]
    assert "photo1.png" in filenames
    assert "document.docx" in filenames


def test_unauthorized_user_cannot_download_or_access_attachment(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
    second_auth_headers: dict,
):
    """6. Verify unauthorized user cannot download or access another user's attachment."""
    # User A uploads attachment
    upload_res = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("confidential.pdf", io.BytesIO(b"%PDF confidential"), "application/pdf")},
    )
    assert upload_res.status_code == 201
    attachment_id = upload_res.json()["id"]

    # User B tries to download User A's attachment -> 403
    download_res = client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=second_auth_headers,
    )
    assert download_res.status_code == 403

    # User B tries to list User A's challenge attachments -> 403
    list_res = client.get(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=second_auth_headers,
    )
    assert list_res.status_code == 403


def test_attachment_deletion_removes_record_safely(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
    temp_upload_dir: Path,
):
    """7. Verify owner can delete attachment and physical file is unlinked."""
    upload_res = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("to_delete.pdf", io.BytesIO(b"%PDF delete me"), "application/pdf")},
    )
    assert upload_res.status_code == 201
    attachment_id = upload_res.json()["id"]

    # Verify physical file exists
    files_before = list(temp_upload_dir.glob("*.pdf"))
    assert len(files_before) == 1

    # Delete attachment
    del_res = client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=auth_headers,
    )
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verify physical file unlinked
    files_after = list(temp_upload_dir.glob("*.pdf"))
    assert len(files_after) == 0

    # Verify second delete returns 404
    del_res_again = client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=auth_headers,
    )
    assert del_res_again.status_code == 404


def test_missing_physical_file_handled_gracefully(
    client: TestClient,
    test_challenge: Challenge,
    auth_headers: dict,
    temp_upload_dir: Path,
):
    """8. Verify deleting an attachment when physical file was already deleted does not crash."""
    upload_res = client.post(
        f"/api/v1/challenges/{test_challenge.id}/attachments",
        headers=auth_headers,
        files={"file": ("ghost.pdf", io.BytesIO(b"%PDF ghost"), "application/pdf")},
    )
    assert upload_res.status_code == 201
    attachment_id = upload_res.json()["id"]

    # Manually delete the physical file before calling delete API
    for f in temp_upload_dir.glob("*.pdf"):
        f.unlink()

    # Call delete API -> must handle missing physical file gracefully without crashing (HTTP 200)
    del_res = client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=auth_headers,
    )
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True
