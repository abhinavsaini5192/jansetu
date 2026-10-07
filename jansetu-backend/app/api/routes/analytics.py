"""
Platform Analytics and Governance Reporting Routes (Phase 3.8).
Database-backed aggregation endpoints for challenges, institutional projects, and field impact.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    ChallengesAnalyticsResponse,
    DistrictAnalyticsItem,
    DomainAnalyticsItem,
    ImpactAnalyticsResponse,
    ProjectsAnalyticsResponse,
)
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Platform Analytics Overview",
)
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AnalyticsOverviewResponse:
    return analytics_service.get_overview(db)


@router.get(
    "/challenges",
    response_model=ChallengesAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Challenges Analytics Breakdown",
)
def get_challenges_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ChallengesAnalyticsResponse:
    return analytics_service.get_challenges_analytics(db)


@router.get(
    "/projects",
    response_model=ProjectsAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Projects Execution Analytics",
)
def get_projects_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ProjectsAnalyticsResponse:
    return analytics_service.get_projects_analytics(db)


@router.get(
    "/impact",
    response_model=ImpactAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Verified Societal Impact Analytics",
)
def get_impact_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ImpactAnalyticsResponse:
    return analytics_service.get_impact_analytics(db)


@router.get(
    "/districts",
    response_model=List[DistrictAnalyticsItem],
    status_code=status.HTTP_200_OK,
    summary="Get District-wise Civic Analytics",
)
def get_districts_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> List[DistrictAnalyticsItem]:
    return analytics_service.get_districts_analytics(db)


@router.get(
    "/domains",
    response_model=List[DomainAnalyticsItem],
    status_code=status.HTTP_200_OK,
    summary="Get Sectoral Domain Analytics",
)
def get_domains_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> List[DomainAnalyticsItem]:
    return analytics_service.get_domains_analytics(db)
