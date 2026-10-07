from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import ProposalStatus


class ProposalCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: str = Field(..., min_length=10, description="Executive solution summary")
    detailed_description: str = Field(..., min_length=20, description="Full technical breakdown")
    methodology: Optional[str] = Field(None, description="Engineering/research approach")
    expected_outcomes: Optional[str] = Field(None, description="Anticipated civic and technical results")
    estimated_budget: Optional[str] = Field(None, max_length=100)
    required_resources: Optional[str] = Field(None, description="Lab, field, or computing requirements")
    implementation_timeline: Optional[str] = Field(None, description="Phase timeline breakdown")
    submitted_by_team_id: Optional[str] = None


class ProposalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    summary: Optional[str] = Field(None, min_length=10)
    detailed_description: Optional[str] = Field(None, min_length=20)
    methodology: Optional[str] = None
    expected_outcomes: Optional[str] = None
    estimated_budget: Optional[str] = None
    required_resources: Optional[str] = None
    implementation_timeline: Optional[str] = None


class ProposalReviewRequest(BaseModel):
    decision: str = Field(
        ...,
        pattern="^(approve|reject|request_revision|move_to_review)$",
        description="Official review decision",
    )
    review_comment: Optional[str] = Field(None, max_length=2000)


class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    submitted_by_team_id: Optional[str] = None
    title: str
    summary: str
    detailed_description: str
    methodology: Optional[str] = None
    expected_outcomes: Optional[str] = None
    estimated_budget: Optional[str] = None
    required_resources: Optional[str] = None
    implementation_timeline: Optional[str] = None
    status: ProposalStatus
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_user_id: Optional[str] = None
    review_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProposalHistoryItem(BaseModel):
    action: str
    timestamp: datetime
    actor_name: Optional[str] = None
    notes: Optional[str] = None
