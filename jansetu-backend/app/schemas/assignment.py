from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator

from app.utils.enums import AssignmentStatus


class AssignmentCreate(BaseModel):
    university_id: Optional[str] = None
    universityId: Optional[str] = None
    department_id: Optional[str] = None
    departmentId: Optional[str] = None
    invitation_message: Optional[str] = None

    @model_validator(mode="after")
    def resolve_identifiers(self) -> "AssignmentCreate":
        target_uni = self.university_id or self.universityId
        if not target_uni:
            raise ValueError("university_id or universityId is required")
        self.university_id = target_uni
        self.department_id = self.department_id or self.departmentId
        return self


class AssignmentAcceptRequest(BaseModel):
    response_message: Optional[str] = None


class AssignmentDeclineRequest(BaseModel):
    response_message: Optional[str] = None


class AssignmentCancelRequest(BaseModel):
    reason: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: str
    challenge_id: str
    university_id: str
    university_name: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    assigned_by_user_id: str
    status: AssignmentStatus
    invitation_message: Optional[str] = None
    response_message: Optional[str] = None
    assigned_at: datetime
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
