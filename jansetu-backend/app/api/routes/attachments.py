"""
Challenge Attachment API Routes.
Provides multipart upload, listing, authorized secure download, and deletion
for files attached to societal challenges.
"""
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.attachment import AttachmentListResponse, AttachmentResponse
from app.schemas.common import ApiResponse
from app.services.attachment_service import attachment_service

router = APIRouter()


@router.post(
    "/challenges/{challenge_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Challenge Attachment",
    description="Uploads a supporting file (image, PDF, doc) for a specific challenge via multipart/form-data.",
)
def upload_challenge_attachment(
    challenge_id: str,
    file: UploadFile = File(..., description="The binary file to upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> AttachmentResponse:
    """Upload supporting document or photo for a challenge."""
    attachment = attachment_service.upload_attachment(
        db=db,
        challenge_id=challenge_id,
        upload_file=file,
        current_user=current_user,
    )
    return AttachmentResponse.model_validate(attachment)


@router.get(
    "/challenges/{challenge_id}/attachments",
    response_model=AttachmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Challenge Attachments",
    description="Lists all file attachments associated with a challenge. Caller must be authorized.",
)
def list_challenge_attachments(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> AttachmentListResponse:
    """List attachments associated with a challenge."""
    items = attachment_service.list_attachments(
        db=db,
        challenge_id=challenge_id,
        current_user=current_user,
    )
    serialized = [AttachmentResponse.model_validate(item) for item in items]
    return AttachmentListResponse(items=serialized, total=len(serialized))


@router.get(
    "/attachments/{attachment_id}/download",
    summary="Download Attachment",
    description="Securely streams the attachment binary file. Requires caller authorization.",
    response_class=FileResponse,
)
def download_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> FileResponse:
    """Download physical attachment file."""
    attachment = attachment_service.get_attachment_for_download(
        db=db,
        attachment_id=attachment_id,
        current_user=current_user,
    )
    return FileResponse(
        path=attachment.storage_path,
        media_type=attachment.mime_type,
        filename=attachment.original_filename,
    )


@router.delete(
    "/attachments/{attachment_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Attachment",
    description="Permanently deletes the attachment record and unlinks its physical file on disk.",
)
def delete_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> ApiResponse[dict]:
    """Delete an attachment."""
    attachment_service.delete_attachment(
        db=db,
        attachment_id=attachment_id,
        current_user=current_user,
    )
    return ApiResponse(
        success=True,
        message="Attachment deleted successfully.",
        data={"id": attachment_id},
    )
