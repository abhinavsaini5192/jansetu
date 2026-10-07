"""
Pydantic v2 Schemas for Government Validation Workflow.
Defines payloads and response contracts for official review actions,
department assignments, and decision histories.
"""
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.challenge import ChallengeResponse


class GovernmentDecisionRequest(BaseModel):
    """
    Intake payload for official government decisions on a challenge.
    Maps frontend-friendly aliases (remarks, reason) while enforcing valid decision types.
    """
    decision: str = Field(
        ...,
        description="Decision type: move_to_review, validate, reject, mark_duplicate, request_clarification, assign_department",
    )
    review_comment: Optional[str] = Field(None, description="Official evaluation remarks")
    rejection_reason: Optional[str] = Field(None, description="Detailed explanation if rejected")
    duplicate_of_challenge_id: Optional[str] = Field(None, description="Target challenge UUID if duplicate")
    clarification_request: Optional[str] = Field(None, description="Clarification questions for the citizen")
    department: Optional[str] = Field(None, description="Assigning government department")

    # Compatibility aliases for frontend
    remarks: Optional[str] = Field(None, description="Frontend alias for review_comment")
    reason: Optional[str] = Field(None, description="Frontend alias for rejection_reason")

    @model_validator(mode="before")
    @classmethod
    def map_aliases_and_normalize(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize decision string
            if "decision" in data and isinstance(data["decision"], str):
                data["decision"] = data["decision"].strip().lower()

            # Map frontend aliases
            if not data.get("review_comment") and data.get("remarks"):
                data["review_comment"] = data["remarks"]
            if not data.get("rejection_reason") and data.get("reason"):
                data["rejection_reason"] = data["reason"]

            # If review_comment is still empty but clarification_request provided
            if not data.get("review_comment") and data.get("clarification_request"):
                data["review_comment"] = data["clarification_request"]

            # If review_comment is still empty but rejection_reason provided
            if not data.get("review_comment") and data.get("rejection_reason"):
                data["review_comment"] = data["rejection_reason"]
        return data


class GovernmentReviewResponse(BaseModel):
    """Public representation of a government review record."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    reviewer_user_id: str
    reviewer_name: Optional[str] = None
    previous_status: str
    new_status: str
    validation_status: str
    review_comment: str
    rejection_reason: Optional[str] = None
    duplicate_of_challenge_id: Optional[str] = None
    clarification_request: Optional[str] = None
    reviewed_at: datetime
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_reviewer_name(cls, data: Any) -> Any:
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            reviewer_user = getattr(data, "reviewer_user", None)
            reviewer_name = getattr(reviewer_user, "full_name", None) if reviewer_user else None
            return {
                "id": getattr(data, "id", None),
                "challenge_id": getattr(data, "challenge_id", None),
                "reviewer_user_id": getattr(data, "reviewer_user_id", None),
                "reviewer_name": reviewer_name,
                "previous_status": getattr(data, "previous_status", None),
                "new_status": getattr(data, "new_status", None),
                "validation_status": getattr(data, "validation_status", None),
                "review_comment": getattr(data, "review_comment", ""),
                "rejection_reason": getattr(data, "rejection_reason", None),
                "duplicate_of_challenge_id": getattr(data, "duplicate_of_challenge_id", None),
                "clarification_request": getattr(data, "clarification_request", None),
                "reviewed_at": getattr(data, "reviewed_at", None),
                "created_at": getattr(data, "created_at", None),
            }
        return data


class GovernmentReviewHistoryResponse(BaseModel):
    """List of all review cycles executed on a specific challenge."""
    challenge_id: str
    history: List[GovernmentReviewResponse] = Field(default_factory=list)
    total: int = 0
