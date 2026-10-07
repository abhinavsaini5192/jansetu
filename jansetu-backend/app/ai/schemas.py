"""
Pydantic Schemas for AI Problem Intelligence, Classification,
Semantic Similarity, and Advisory Duplicate Detection.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EntityItem(BaseModel):
    category: str
    value: str


class CapabilityWeight(BaseModel):
    name: str
    weight: int = Field(..., ge=0, le=100)


class SemanticDuplicateItem(BaseModel):
    id: str
    title: str
    similarity: int = Field(..., ge=0, le=100)
    district: Optional[str] = None


class AIAnalysisResult(BaseModel):
    """
    Standard schema for AI / Deterministic Fallback Challenge Analysis.
    Maintains dual compatibility with Phase 3 specifications and React UI.
    """
    challenge_id: str
    detected_domain: str
    detected_subdomain: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    location_entities: List[str] = Field(default_factory=list)
    stakeholder_entities: List[str] = Field(default_factory=list)
    urgency_level: str
    affected_population_summary: Optional[str] = None
    concise_problem_summary: Optional[str] = None
    suggested_tags: List[str] = Field(default_factory=list)
    explanation: str
    provider: str
    fallback_used: bool = True

    # Frontend Screen 03 (3_AiIntelligence.jsx) Compatibility Fields
    status: str = "COMPLETED"
    domain: Optional[str] = None
    subDomain: Optional[str] = None
    domainConfidence: Optional[int] = 85
    priorityScore: Optional[int] = 70
    priorityLevel: Optional[str] = "Normal"
    priorityRationale: Optional[str] = None
    extractedEntities: List[Dict[str, str]] = Field(default_factory=list)
    requiredCapabilities: List[Dict[str, Any]] = Field(default_factory=list)
    semanticDuplicates: List[Dict[str, Any]] = Field(default_factory=list)
    clusterSummary: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class SimilarChallengeItem(BaseModel):
    """Represents a semantically similar challenge match."""
    challenge_id: str
    reference_code: Optional[str] = None
    title: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    similarity_percentage: int = Field(..., ge=0, le=100)
    matching_reasons: List[str] = Field(default_factory=list)
    same_domain: bool = False
    same_district: bool = False
    shared_keywords: List[str] = Field(default_factory=list)
    district: Optional[str] = None
    domain: Optional[str] = None


class SimilarChallengesResponse(BaseModel):
    """Response containing similar challenges found via TF-IDF semantic matching."""
    challenge_id: str
    total_found: int
    similar_challenges: List[SimilarChallengeItem] = Field(default_factory=list)
    disclaimer: str = "Advisory semantic recommendations only. Human verification required."


class DuplicateCheckResponse(BaseModel):
    """Response containing advisory duplicate detection and regional clustering insights."""
    challenge_id: str
    possible_duplicates: List[SimilarChallengeItem] = Field(default_factory=list)
    highest_similarity_score: float = 0.0
    highest_similarity_percentage: int = 0
    confidence_level: str = "LOW"  # LOW | MEDIUM | HIGH
    matching_reasons: List[str] = Field(default_factory=list)
    recommended_action: str
    warning: str = (
        "Advisory recommendation only. Official challenge deduplication, merging, "
        "or rejection strictly requires authorized human government nodal officer review."
    )
    cluster_summary: Optional[str] = None


class ProjectIntelligenceResponse(BaseModel):
    """
    Actionable AI & Rule-based Project Intelligence (Phase 3.9).
    Summarizes execution health, highlights delayed milestones, unresolved risks, and next steps.
    """
    project_id: str
    project_title: str
    project_summary: str
    current_status: str
    completion_percentage: float = 0.0
    milestone_summary: str
    delayed_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    upcoming_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    open_risks: List[Dict[str, Any]] = Field(default_factory=list)
    high_priority_risks: List[Dict[str, Any]] = Field(default_factory=list)
    pending_deliverables: List[Dict[str, Any]] = Field(default_factory=list)
    partner_status_summary: str
    proposal_status: str
    recommended_next_actions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    provider: str = "deterministic-fallback"
    fallback_used: bool = True
    disclaimer: str = "Advisory execution insights only. Project management decisions require human verification."

    model_config = ConfigDict(populate_by_name=True)
