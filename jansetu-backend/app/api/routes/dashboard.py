"""
Dashboard and Platform Statistics API Routes.
Provides real aggregated statistics on challenges, Jharkhand districts,
societal domains, and platform activity.
Derived strictly from PostgreSQL records without mock or fake data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional, require_authenticated_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardDistrictSummaryResponse,
    DashboardDomainSummaryResponse,
    DashboardOverviewResponse,
    DistrictCountItem,
    DomainCountItem,
    RecentActivityItem,
)
from app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard Platform Overview",
    description="Aggregated platform statistics across all challenges and user unread notifications.",
)
@router.get(
    "/challenges-summary",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Challenges Status Summary",
    include_in_schema=True,
)
@router.get(
    "/stats",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard Stats (Frontend Alias)",
    include_in_schema=True,
)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> DashboardOverviewResponse:
    """Retrieve platform aggregate challenge numbers and unread count."""
    return dashboard_service.get_overview(db=db, current_user=current_user)


@router.get(
    "/district-summary",
    response_model=DashboardDistrictSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="District Summary",
    description="Challenge counts and validated counts grouped by Jharkhand district.",
)
def get_district_summary(
    db: Session = Depends(get_db),
) -> DashboardDistrictSummaryResponse:
    """Retrieve counts grouped by district."""
    items = dashboard_service.get_district_summary(db=db)
    return DashboardDistrictSummaryResponse(
        items=items,
        total_districts=len(items),
    )


@router.get(
    "/districts",
    response_model=List[DistrictCountItem],
    status_code=status.HTTP_200_OK,
    summary="District Trends List (Frontend Contract)",
    description="Array of district metrics for frontend map and chart visualizations.",
)
def get_districts_list(
    db: Session = Depends(get_db),
) -> List[DistrictCountItem]:
    """Returns direct list of district counts for frontend hooks."""
    return dashboard_service.get_district_summary(db=db)


@router.get(
    "/domain-summary",
    response_model=DashboardDomainSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Domain Summary",
    description="Challenge counts grouped by societal domain.",
)
def get_domain_summary(
    db: Session = Depends(get_db),
) -> DashboardDomainSummaryResponse:
    """Retrieve counts grouped by societal domain."""
    items = dashboard_service.get_domain_summary(db=db)
    return DashboardDomainSummaryResponse(
        items=items,
        total_domains=len(items),
    )


@router.get(
    "/domains",
    response_model=List[DomainCountItem],
    status_code=status.HTTP_200_OK,
    summary="Domain Breakdown List (Frontend Contract)",
    description="Array of domain breakdown metrics for charts.",
)
def get_domains_list(
    db: Session = Depends(get_db),
) -> List[DomainCountItem]:
    """Returns direct list of domain metrics for frontend hooks."""
    return dashboard_service.get_domain_summary(db=db)


@router.get(
    "/activity",
    response_model=List[RecentActivityItem],
    status_code=status.HTTP_200_OK,
    summary="Recent Activity Feed",
    description="Recent platform events derived from immutable audit logs.",
)
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Max activities to return"),
    db: Session = Depends(get_db),
) -> List[RecentActivityItem]:
    """Fetch recent activity timeline."""
    return dashboard_service.get_recent_activity(db=db, limit=limit)
