from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExplainableFactor(BaseModel):
    label: str
    score: int
    reason: str


class UniversityMatchResult(BaseModel):
    # Standard backend fields
    university_id: str
    university_name: str
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    score: int = Field(..., ge=0, le=100)
    total_score: float = Field(default=0.0)
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    reasons: List[str] = Field(default_factory=list)
    match_reasons: List[str] = Field(default_factory=list)
    matched_domains: List[str] = Field(default_factory=list)
    matched_capabilities: List[str] = Field(default_factory=list)
    missing_capabilities: List[str] = Field(default_factory=list)
    explanation: str = ""
    district_match: bool = False
    eligibility_status: str = "ELIGIBLE"
    data_source: str = "explainable-hybrid-matching"

    # Frontend compatibility properties (Screen 05 • 5_UniversityMatching.jsx)
    id: Optional[str] = None
    universityId: Optional[str] = None
    name: Optional[str] = None
    overallMatch: Optional[int] = None
    location: Optional[str] = None
    type: Optional[str] = None
    accreditation: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    explainableFactors: Dict[str, ExplainableFactor] = Field(default_factory=dict)


class MatchingResponse(BaseModel):
    challenge_id: str
    challenge_title: str
    challenge_domain: str
    challenge_district: str
    total_candidates: int
    matches: List[UniversityMatchResult]
    disclaimer: str = "Advisory recommendation only. Government users make all official mandate decisions."
