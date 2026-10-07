from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import DeliverableStatus, MilestoneStatus


class DeliverableCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    file_attachment_id: Optional[str] = Field(None, description="Linked existing attachment UUID")


class DeliverableUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    file_attachment_id: Optional[str] = None


class DeliverableReviewRequest(BaseModel):
    decision: str = Field(..., pattern="^(accept|reject|request_revision)$")
    review_comment: Optional[str] = Field(None, max_length=2000)


class DeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    milestone_id: str
    title: str
    description: Optional[str] = None
    file_attachment_id: Optional[str] = None
    submitted_by_user_id: str
    status: DeliverableStatus
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_user_id: Optional[str] = None
    review_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MilestoneCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    sequence_number: int = Field(default=1, ge=1)
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)


class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    sequence_number: Optional[int] = Field(None, ge=1)
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: Optional[MilestoneStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    progress: Optional[int] = Field(None, ge=0, le=100, description="Frontend alias for completion_percentage")


class MilestoneStatusUpdate(BaseModel):
    status: MilestoneStatus
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    sequence_number: int
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: MilestoneStatus
    completion_percentage: int
    progress: int = 0
    dueDate: Optional[str] = None
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime
    deliverables: List[DeliverableResponse] = []
