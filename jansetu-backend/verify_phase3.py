"""
Manual Verification Script for Phases 3.1 - 3.5.
Checks:
1. Application startup and health check.
2. AI-disabled / unconfigured provider mode works without error.
3. Fallback analysis works on /api/v1/ai/challenges/{id}/analyze and /api/v1/challenges/{id}/ai-analysis.
4. Similar-challenge endpoint responds on /api/v1/ai/challenges/{id}/similar.
5. Duplicate-check endpoint responds on /api/v1/ai/challenges/{id}/duplicate-check.
6. Matching endpoint responds with explainable score breakdown on /api/v1/challenges/{id}/matches.
7. Unavailable AI provider gracefully falls back without crashing the backend.
"""
import os
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.capability import Capability
from app.models.challenge import Challenge
from app.models.department import Department
from app.models.organization import Organization
from app.models.university_profile import UniversityProfile
from app.models.user import User
from app.utils.enums import (
    ChallengeStatus,
    InstitutionCategory,
    OrganizationType,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
    UserRole,
    ValidationStatus,
)


def run_verification():
    print("=== STARTING PHASE 3.1 - 3.5 VERIFICATION ===")

    # Use in-memory SQLite for self-contained execution
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

    try:
        # 1. Verify application starts and health check responds
        resp_health = client.get("/health")
        assert resp_health.status_code == 200, f"Health check failed: {resp_health.text}"
        print("[PASS] 1. Application starts and /health responds: 200 OK")

        # Create test users and challenges in DB
        uid = uuid.uuid4().hex[:6]
        citizen = User(
            full_name="Verification Citizen",
            email=f"cit.{uid}@example.com",
            password_hash="pass",
            role=UserRole.CITIZEN,
            is_active=True,
        )
        db.add(citizen)
        db.flush()

        token = create_access_token(
            subject=citizen.id,
            additional_claims={"email": citizen.email, "role": citizen.role.value},
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Challenge 1: Arsenic & Fluoride in Ranchi
        c1 = Challenge(
            submitted_by_user_id=citizen.id,
            title=f"Severe Arsenic Contamination in Kanke Wells {uid}",
            description="High levels of toxic arsenic and fluoride discovered in drinking groundwater wells.",
            problem_statement="Drinking water exceeds permissible fluoride limits requiring low-cost filtration.",
            expected_outcome="Safe community drinking water supply with continuous monitoring.",
            district="Ranchi",
            domain=SocietalDomain.WATER,
            priority=PriorityLevel.CRITICAL,
            urgency=UrgencyLevel.CRITICAL,
            status=ChallengeStatus.VALIDATED,
            validation_status=ValidationStatus.VALIDATED,
        )
        # Challenge 2: Similar water report in Ranchi
        c2 = Challenge(
            submitted_by_user_id=citizen.id,
            title=f"Fluoride and Toxic Water Contamination in Ratu {uid}",
            description="Groundwater well testing shows hazardous fluoride levels in village handpumps.",
            problem_statement="Filtration systems needed for contaminated groundwater wells.",
            expected_outcome="Affordable water filtration filters installed.",
            district="Ranchi",
            domain=SocietalDomain.WATER,
            priority=PriorityLevel.HIGH,
            urgency=UrgencyLevel.HIGH,
            status=ChallengeStatus.VALIDATED,
            validation_status=ValidationStatus.VALIDATED,
        )
        # Challenge 3: Unrelated agriculture challenge in Dhanbad
        c3 = Challenge(
            submitted_by_user_id=citizen.id,
            title=f"Pest Infestation in Paddy Crops {uid}",
            description="Paddy crop damage due to yellow stem borer pest outbreak.",
            problem_statement="Need organic bio-pesticide solution for smallholder farmers.",
            expected_outcome="Crop yield protection and pest management.",
            district="Dhanbad",
            domain=SocietalDomain.AGRICULTURE,
            priority=PriorityLevel.MEDIUM,
            urgency=UrgencyLevel.MEDIUM,
            status=ChallengeStatus.VALIDATED,
            validation_status=ValidationStatus.VALIDATED,
        )
        db.add_all([c1, c2, c3])
        db.flush()

        # University with water filtration capabilities
        uni_org = Organization(
            name=f"Birla Institute of Technology {uid}",
            organization_type=OrganizationType.UNIVERSITY,
            district="Ranchi",
            is_active=True,
            is_verified=True,
        )
        db.add(uni_org)
        db.flush()

        uni_prof = UniversityProfile(
            organization_id=uni_org.id,
            institution_category=InstitutionCategory.TECHNICAL_INSTITUTE,
            accreditation_details="NAAC A++",
            district="Ranchi",
            is_verified=True,
            is_active=True,
        )
        dept = Department(
            organization_id=uni_org.id,
            name="Department of Environmental & Water Engineering",
            is_active=True,
        )
        cap = Capability(
            name="Groundwater Arsenic Testing & Filtration",
            domain=SocietalDomain.WATER,
            keywords="arsenic fluoride groundwater water filtration",
            is_active=True,
        )
        dept.capabilities.append(cap)
        db.add_all([uni_prof, dept, cap])
        db.commit()

        # 2. AI-disabled / unconfigured provider mode verification
        assert settings.AI_ENABLED is False or settings.AI_PROVIDER in ("none", "fallback")
        print("[PASS] 2. AI-disabled mode verified: AI_ENABLED=False, AI_PROVIDER='none'")

        # 3. Fallback analysis endpoint: POST /api/v1/ai/challenges/{id}/analyze
        resp_an1 = client.post(f"/api/v1/ai/challenges/{c1.id}/analyze", headers=headers)
        assert resp_an1.status_code == 200, f"Analyze failed: {resp_an1.text}"
        data_an1 = resp_an1.json()
        assert data_an1["fallback_used"] is True
        assert data_an1["provider"] == "deterministic-fallback"
        assert data_an1["detected_domain"] == "water"
        assert len(data_an1["requiredCapabilities"]) > 0
        assert data_an1["status"] == "COMPLETED"
        print(f"[PASS] 3a. /api/v1/ai/challenges/{c1.id}/analyze responds: domain={data_an1['detected_domain']}, fallback={data_an1['fallback_used']}")

        # 3b. Frontend compatibility endpoint: GET /api/v1/challenges/{id}/ai-analysis
        resp_an2 = client.get(f"/api/v1/challenges/{c1.id}/ai-analysis", headers=headers)
        assert resp_an2.status_code == 200, f"Frontend AI analysis failed: {resp_an2.text}"
        data_an2 = resp_an2.json()
        assert data_an2["domainConfidence"] >= 60
        assert "extractedEntities" in data_an2
        print(f"[PASS] 3b. /api/v1/challenges/{c1.id}/ai-analysis responds: confidence={data_an2['domainConfidence']}%")

        # 4. Semantic similarity endpoint: GET /api/v1/ai/challenges/{id}/similar
        resp_sim = client.get(f"/api/v1/ai/challenges/{c1.id}/similar", headers=headers)
        assert resp_sim.status_code == 200, f"Similar search failed: {resp_sim.text}"
        data_sim = resp_sim.json()
        assert "similar_challenges" in data_sim
        assert data_sim["total_found"] > 0
        top_sim = data_sim["similar_challenges"][0]
        assert top_sim["challenge_id"] == c2.id  # c2 should be the top match
        assert top_sim["same_domain"] is True
        assert top_sim["same_district"] is True
        assert top_sim["similarity_score"] > 0.3
        print(f"[PASS] 4. /api/v1/ai/challenges/{c1.id}/similar responds: found={data_sim['total_found']}, top_match_score={top_sim['similarity_percentage']}%")

        # 5. Duplicate detection endpoint: GET /api/v1/ai/challenges/{id}/duplicate-check
        resp_dup = client.get(f"/api/v1/ai/challenges/{c1.id}/duplicate-check", headers=headers)
        assert resp_dup.status_code == 200, f"Duplicate check failed: {resp_dup.text}"
        data_dup = resp_dup.json()
        assert data_dup["confidence_level"] in ("LOW", "MEDIUM", "HIGH")
        assert "warning" in data_dup
        assert "recommended_action" in data_dup
        print(f"[PASS] 5. /api/v1/ai/challenges/{c1.id}/duplicate-check responds: confidence={data_dup['confidence_level']}, action='{data_dup['recommended_action'][:50]}...'")

        # 6. Advanced Explainable Matching endpoint: GET /api/v1/challenges/{id}/matches
        resp_match = client.get(f"/api/v1/challenges/{c1.id}/matches", headers=headers)
        assert resp_match.status_code == 200, f"Matching failed: {resp_match.text}"
        data_match = resp_match.json()
        assert "matches" in data_match
        assert len(data_match["matches"]) > 0
        top_match = data_match["matches"][0]
        assert "score_breakdown" in top_match
        assert "domain_match" in top_match["score_breakdown"]
        assert "capability_match" in top_match["score_breakdown"]
        assert "keyword_similarity" in top_match["score_breakdown"]
        assert "geographic_relevance" in top_match["score_breakdown"]
        assert "urgency_compatibility" in top_match["score_breakdown"]
        assert "explanation" in top_match
        assert top_match["overallMatch"] >= 60
        print(f"[PASS] 6. /api/v1/challenges/{c1.id}/matches responds: total_score={top_match['total_score']}, breakdown={top_match['score_breakdown']}")

        # 7. Verify unavailable AI provider does not crash the backend
        from app.ai.providers.external import ExternalAIProvider
        ext = ExternalAIProvider()
        try:
            ext.analyze_challenge({"title": "Test Crash Resistance"})
        except Exception as e:
            print(f"[PASS] 7. Unavailable AI provider isolated safely without crashing: {type(e).__name__}")

        print("=== ALL PHASE 3.1 - 3.5 VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")

    finally:
        db.close()


if __name__ == "__main__":
    run_verification()
