"""
Pydantic v2 Schemas for Platform Dashboard & Aggregations.
Provides summarized metrics for citizens, nodal officers, and executives,
calculated from real database records.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class DistrictCountItem(BaseModel):
    """Aggregation count per Jharkhand district."""
    district: str
    count: int
    validated_count: int = 0


class DomainCountItem(BaseModel):
    """Aggregation count per societal domain."""
    domain: str
    count: int
    label: Optional[str] = None


class RecentActivityItem(BaseModel):
    """Summary representation of recent platform activities."""
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime


class DashboardOverviewResponse(BaseModel):
    """
    Consolidated platform metrics representation.
    Provides snake_case fields as well as frontend camelCase aliases.
    """
    total_challenges: int = 0
    submitted_challenges: int = 0
    under_review_challenges: int = 0
    validated_challenges: int = 0
    rejected_challenges: int = 0
    duplicate_challenges: int = 0
    clarification_needed_challenges: int = 0
    assigned_challenges: int = 0
    unread_notifications_count: int = 0

    # Frontend camelCase compatibility
    totalChallenges: int = 0
    underReview: int = 0
    validated: int = 0
    rejected: int = 0
    pending: int = 0

    @model_validator(mode="before")
    @classmethod
    def populate_camel_case(cls, data: Any) -> Any:
        if isinstance(data, dict):
            tot = data.get("total_challenges", 0)
            sub = data.get("submitted_challenges", 0)
            ur = data.get("under_review_challenges", 0)
            val = data.get("validated_challenges", 0)
            rej = data.get("rejected_challenges", 0)

            data["totalChallenges"] = tot
            data["underReview"] = ur
            data["validated"] = val
            data["rejected"] = rej
            data["pending"] = sub + ur
        return data


class DashboardDistrictSummaryResponse(BaseModel):
    """Listing of district metrics."""
    items: List[DistrictCountItem] = Field(default_factory=list)
    total_districts: int = 0


class DashboardDomainSummaryResponse(BaseModel):
    """Listing of domain metrics."""
    items: List[DomainCountItem] = Field(default_factory=list)
    total_domains: int = 0
