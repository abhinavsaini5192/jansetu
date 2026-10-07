"""
AI Problem Intelligence & Semantic Similarity Routing (Phases 3.1 – 3.4).
Endpoints for AI challenge analysis, entity extraction, TF-IDF semantic similarity,
and advisory duplicate detection.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.ai.duplicate import duplicate_service
from app.ai.schemas import (
    AIAnalysisResult,
    DuplicateCheckResponse,
    ProjectIntelligenceResponse,
    SimilarChallengesResponse,
)
from app.ai.service import ai_service
from app.ai.similarity import similarity_service
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user_optional
from app.models.user import User

router = APIRouter()


@router.post(
    "/challenges/{challenge_id}/analyze",
    response_model=AIAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze Challenge via AI / Fallback",
    description=(
        "Executes AI problem classification, entity extraction, and capability weighting. "
        "Automatically falls back to transparent deterministic analysis if AI is unavailable or disabled. "
        "Strictly advisory: does not mutate official challenge validation status."
    ),
)
def analyze_challenge(
    challenge_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AIAnalysisResult:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ai_service.analyze_challenge_by_id(
        db=db,
        challenge_id=challenge_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get(
    "/challenges/{challenge_id}/similar",
    response_model=SimilarChallengesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Semantically Similar Challenges",
    description=(
        "Calculates TF-IDF cosine similarity and multi-field proximity against existing challenges. "
        "Excludes the target challenge itself. Advisory recommendations only."
    ),
)
def get_similar_challenges(
    challenge_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    minimum_score: float = Query(default=0.20, ge=0.0, le=1.0),
    same_district_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> SimilarChallengesResponse:
    return similarity_service.find_similar_challenges(
        db=db,
        challenge_id=challenge_id,
        limit=limit,
        minimum_score=minimum_score,
        same_district_only=same_district_only,
    )


@router.get(
    "/challenges/{challenge_id}/duplicate-check",
    response_model=DuplicateCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Advisory Challenge Duplicate Detection",
    description=(
        "Evaluates potential duplication against deterministic similarity thresholds. "
        "Returns advisory confidence levels (LOW/MEDIUM/HIGH) and recommended actions. "
        "Never mutates challenge status; official decisions strictly require human government review."
    ),
)
def check_challenge_duplicates(
    challenge_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    minimum_score: float = Query(default=0.35, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> DuplicateCheckResponse:
    return duplicate_service.check_duplicates(
        db=db,
        challenge_id=challenge_id,
        limit=limit,
        minimum_score=minimum_score,
    )


@router.get(
    "/projects/{project_id}/intelligence",
    response_model=ProjectIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Actionable AI Project Intelligence",
    description=(
        "Synthesizes milestone progress, risk severity, deliverable status, and next steps "
        "using real database records. Advisory only; does not mutate project state."
    ),
)
def get_project_intelligence(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
) -> ProjectIntelligenceResponse:
    from app.ai.project_intelligence import project_intelligence_service
    return project_intelligence_service.analyze_project(db=db, project_id=project_id)
