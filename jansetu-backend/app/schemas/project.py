from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.enums import ProjectStatus


class ProjectCreate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    challenge_id: Optional[str] = None
    challengeId: Optional[str] = None
    university_id: Optional[str] = None
    institutionName: Optional[str] = None
    department_id: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    lead_faculty: Optional[str] = None
    leadFaculty: Optional[str] = None
    student_lead: Optional[str] = None
    studentLead: Optional[str] = None
    budget: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None

    @model_validator(mode="after")
    def normalize_fields(self) -> "ProjectCreate":
        self.title = self.title or self.name or "Untitled Project"
        self.challenge_id = self.challenge_id or self.challengeId
        self.description = self.description or self.summary
        self.lead_faculty = self.lead_faculty or self.leadFaculty
        self.student_lead = self.student_lead or self.studentLead
        return self


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    lead_faculty: Optional[str] = None
    student_lead: Optional[str] = None
    budget: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: str
    project_code: str
    challenge_id: str
    assignment_id: Optional[str] = None
    university_id: str
    department_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ProjectStatus
    created_by_user_id: str
    lead_faculty: Optional[str] = None
    student_lead: Optional[str] = None
    budget: Optional[str] = None
    progress_percentage: int = 0
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Frontend camelCase & display compatibility
    code: Optional[str] = None
    name: Optional[str] = None
    institutionName: Optional[str] = None
    department: Optional[str] = None
    progressPercentage: Optional[int] = None
    leadFaculty: Optional[str] = None
    studentLead: Optional[str] = None
    currentStage: Optional[str] = None
    proposalSummary: Optional[str] = None
    teamMembers: List[Dict[str, Any]] = []
    milestones: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)
