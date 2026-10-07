from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import TeamRole


class TeamMemberAdd(BaseModel):
    user_id: str = Field(..., description="ID of user belonging to the project university")
    role: TeamRole = Field(default=TeamRole.STUDENT, description="Multidisciplinary role")


class TeamMemberUpdate(BaseModel):
    role: Optional[TeamRole] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_id: str
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    role: TeamRole
    joined_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TeamCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(default="Core Project Team", max_length=255, description="Team designation")
    description: Optional[str] = Field(None, max_length=1000)
    teamMembers: Optional[List[dict]] = None
    members: Optional[List[dict]] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = []
