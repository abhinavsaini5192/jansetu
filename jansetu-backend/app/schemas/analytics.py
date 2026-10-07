"""
Pydantic Schemas for Platform Analytics & Aggregation (Phase 3.8).
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyticsOverviewResponse(BaseModel):
    total_challenges: int = 0
    validated_challenges: int = 0
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    total_universities: int = 0
    total_partners: int = 0
    total_impact_records: int = 0
    verified_impact_records: int = 0
    challenges_by_status: Dict[str, int] = Field(default_factory=dict)
    projects_by_status: Dict[str, int] = Field(default_factory=dict)
    impact_by_status: Dict[str, int] = Field(default_factory=dict)


class ChallengesAnalyticsResponse(BaseModel):
    total_challenges: int = 0
    validated_challenges: int = 0
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_domain: Dict[str, int] = Field(default_factory=dict)
    by_district: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_urgency: Dict[str, int] = Field(default_factory=dict)


class ProjectsAnalyticsResponse(BaseModel):
    total_projects: int = 0
    by_status: Dict[str, int] = Field(default_factory=dict)
    total_proposals: int = 0
    accepted_proposals: int = 0
    total_milestones: int = 0
    completed_milestones: int = 0
    active_risks_count: int = 0
    total_partnerships: int = 0


class ImpactAnalyticsResponse(BaseModel):
    total_impact_records: int = 0
    verified_impact_records: int = 0
    total_villages_covered: int = 0
    by_impact_type: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    verified_percentage: float = 0.0


class DistrictAnalyticsItem(BaseModel):
    district: str
    total_challenges: int = 0
    validated_challenges: int = 0
    active_projects: int = 0
    villages_covered: int = 0


class DomainAnalyticsItem(BaseModel):
    domain: str
    total_challenges: int = 0
    validated_challenges: int = 0
    active_projects: int = 0
    impact_records: int = 0
