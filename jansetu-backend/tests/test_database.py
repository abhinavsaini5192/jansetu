import os
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.config import Settings, settings
from app.core.database import (
    Base,
    SessionLocal,
    check_database_connection,
    get_db,
)
from app.main import app
from fastapi.testclient import TestClient


def test_database_settings_load_correctly():
    """1. Verify that database pool and runtime settings load properly."""
    assert isinstance(settings.DB_POOL_SIZE, int)
    assert settings.DB_POOL_SIZE > 0
    assert isinstance(settings.DB_MAX_OVERFLOW, int)
    assert isinstance(settings.DB_POOL_TIMEOUT, int)
    assert isinstance(settings.DB_POOL_RECYCLE, int)
    assert isinstance(settings.DB_ECHO, bool)


def test_database_url_read_and_masked():
    """2. Verify that DATABASE_URL is read and masked_database_url safely hides credentials."""
    assert settings.DATABASE_URL.startswith(("postgresql", "sqlite"))
    assert "password" not in settings.masked_database_url
    assert "****" in settings.masked_database_url or "sqlite" in settings.masked_database_url


def test_sessionlocal_configuration():
    """3. Verify that SessionLocal exists and is configured as a session factory."""
    assert callable(SessionLocal)
    session = SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_get_db_session_lifecycle():
    """4. Verify that get_db yields a session and closes it cleanly."""
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    # Closing generator executes finally block
    with pytest.raises(StopIteration):
        next(gen)


def test_check_database_connection_unavailable_safe():
    """5. Verify that database health helper handles an unavailable database safely without raising."""
    with patch("app.core.database.engine.connect", side_effect=Exception("Connection refused to 5432")):
        result = check_database_connection()
        assert isinstance(result, dict)
        assert result["status"] == "disconnected"
        assert "unreachable or offline" in result["message"]
        # Ensure raw unmasked password is not leaked in error detail
        assert "password" not in result.get("error_detail", "").lower()


def test_check_database_connection_connected():
    """6. Verify that database health helper returns connected when connection succeeds."""
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    with patch("app.core.database.engine.connect", return_value=mock_conn):
        result = check_database_connection()
        assert isinstance(result, dict)
        assert result["status"] == "connected"
        assert result["message"] == "Database operational"


def test_alembic_config_imports_successfully():
    """7. Verify that Alembic configuration loads properly from alembic.ini."""
    ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
    assert os.path.exists(ini_path)
    alembic_cfg = Config(ini_path)
    script = ScriptDirectory.from_config(alembic_cfg)
    # Check that script directory is detected
    assert script.dir is not None
    # Check baseline revision exists
    revisions = list(script.walk_revisions())
    assert len(revisions) >= 1
    assert revisions[-1].revision == "0001_baseline"


def test_alembic_target_metadata_configured():
    """8. Verify that Alembic env.py targets the shared Base.metadata and loads settings dynamically."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic", "env.py")
    assert os.path.exists(env_path)
    with open(env_path, "r", encoding="utf-8") as f:
        env_source = f.read()

    assert "target_metadata = Base.metadata" in env_source
    assert 'config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)' in env_source
    assert "Base" in env_source


def test_no_business_tables_prematurely_created():
    """9. Verify that Base.metadata contains only Phase 1.4-2.10 tables (no Phase 2.11+ or Phase 3 tables)."""
    expected = {
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
    assert set(Base.metadata.tables.keys()) == expected, f"Only {expected} tables should be registered in Phases 1-2.10"



def test_app_starts_and_handles_offline_db():
    """10. Verify that app starts and system status reports clean status when DB is offline."""
    client = TestClient(app)
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "database" in data["data"]
    assert data["data"]["database"]["status"] in ("connected", "disconnected")


def test_database_url_validation():
    """Verify that invalid database schemes are rejected by Pydantic validation."""
    with pytest.raises(ValueError, match="Invalid database scheme"):
        Settings(DATABASE_URL="ftp://invalid-server/db")
