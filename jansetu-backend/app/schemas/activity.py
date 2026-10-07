from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    actor_user_id: Optional[str] = None
    actor_name: Optional[str] = None
    activity_type: str
    title: str
    description: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime
