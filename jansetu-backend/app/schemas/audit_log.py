"""
Pydantic v2 Schemas for Platform Audit Logs.
Ensures security, compliance, and transparency for system events.
Never exposes sensitive credentials or secret tokens.
"""
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuditLogResponse(BaseModel):
    """Public representation of an immutable audit record."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_user_id: Optional[str] = None
    actor_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    description: str
    metadata_json: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_actor_name(cls, data: Any) -> Any:
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            actor_user = getattr(data, "actor", None)
            actor_name = getattr(actor_user, "full_name", None) if actor_user else None
            return {
                "id": getattr(data, "id", None),
                "actor_user_id": getattr(data, "actor_user_id", None),
                "actor_name": actor_name,
                "action": getattr(data, "action", None),
                "entity_type": getattr(data, "entity_type", None),
                "entity_id": getattr(data, "entity_id", None),
                "description": getattr(data, "description", None),
                "metadata_json": getattr(data, "metadata_json", None),
                "ip_address": getattr(data, "ip_address", None),
                "created_at": getattr(data, "created_at", None),
            }
        return data


class AuditLogListResponse(BaseModel):
    """Paginated listing of audit log entries."""
    items: List[AuditLogResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
