"""
Pydantic Schemas for Challenge File Attachments.
Defines public API response contracts for uploaded supporting files,
ensuring internal storage paths and sensitive server filesystem details
are never exposed.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttachmentResponse(BaseModel):
    """Public representation of an attachment."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique attachment ID")
    challenge_id: str = Field(..., description="Associated challenge UUID")
    uploaded_by_user_id: str = Field(..., description="User UUID who uploaded the file")
    original_filename: str = Field(..., description="Sanitized original filename")
    mime_type: str = Field(..., description="MIME content type")
    file_size: int = Field(..., description="File size in bytes")
    file_extension: str = Field(..., description="File extension")
    created_at: datetime = Field(..., description="Upload timestamp")
    download_url: Optional[str] = Field(None, description="Public download endpoint URL")

    @model_validator(mode="after")
    def ensure_download_url(self) -> "AttachmentResponse":
        if not self.download_url and self.id:
            self.download_url = f"/api/v1/attachments/{self.id}/download"
        return self


class AttachmentListResponse(BaseModel):
    """Listing response for attachments associated with a challenge."""
    items: List[AttachmentResponse] = Field(default_factory=list, description="List of attachments")
    total: int = Field(0, description="Total count of attachments")
