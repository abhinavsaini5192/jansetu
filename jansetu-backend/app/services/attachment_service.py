"""
Attachment Service for JanSetu Platform.
Handles secure file uploads, validation, storage operations, database records,
and authorized access/downloads for supporting evidence and challenge documents.
"""
import mimetypes
import os
import re
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    JanSetuException,
    NotFoundException,
    PayloadTooLargeException,
)
from app.core.logging_config import logger
from app.models.attachment import Attachment
from app.models.challenge import Challenge
from app.models.user import User
from app.repositories.organization_repository import organization_repository
from app.utils.constants import ALLOWED_ATTACHMENT_EXTENSIONS, ALLOWED_ATTACHMENT_MIME_TYPES
from app.utils.enums import UserRole

# Whitelisted extensions (without dot, lowercase)
ALLOWED_EXTENSIONS = {
    ext.lower().lstrip(".") for ext in settings.ALLOWED_UPLOAD_EXTENSIONS
}

# Strictly prohibited dangerous/executable extensions
DANGEROUS_EXTENSIONS = {
    "exe", "sh", "bat", "cmd", "js", "mjs", "php", "py", "dll", "vbs",
    "ps1", "com", "scr", "msi", "jar", "bin", "elf", "so", "app", "apk"
}

# Strict MIME type mapping for whitelisted extensions
MIME_TYPE_MAPPING = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class AttachmentService:
    """Service encapsulating file upload, validation, physical storage, and database persistence."""

    def _get_upload_dir(self) -> Path:
        """Returns resolved Path for configured upload directory, ensuring it exists."""
        upload_dir = Path(settings.UPLOAD_DIR).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    def _sanitize_original_filename(self, filename: Optional[str], default_ext: str) -> str:
        """
        Sanitizes user-provided filename:
        - Strips directory path components (prevents ../ path traversal attacks)
        - Removes control characters and null bytes
        - Ensures safe fallback if filename is blank
        """
        if not filename:
            return f"attachment_{uuid.uuid4().hex[:8]}.{default_ext}"

        # Strip directory separators across Windows and POSIX
        base_name = os.path.basename(filename.replace("\\", "/"))
        # Strip ASCII control characters and null bytes
        cleaned = re.sub(r"[\x00-\x1f\x7f]", "", base_name).strip()
        # Remove any remaining dangerous sequence
        cleaned = cleaned.replace("..", "")
        if not cleaned:
            return f"attachment_{uuid.uuid4().hex[:8]}.{default_ext}"
        return cleaned[:255]

    def validate_file_metadata(
        self,
        original_filename: Optional[str],
        content_type: Optional[str],
    ) -> Tuple[str, str, str]:
        """
        Validates file extension and MIME type.
        Returns tuple of (sanitized_original_filename, clean_extension, validated_mime_type).
        """
        if not original_filename or not original_filename.strip():
            raise BadRequestException("Original filename cannot be empty.")

        # Extract extension
        raw_ext = Path(original_filename).suffix.lower()
        clean_ext = raw_ext.lstrip(".")

        if not clean_ext:
            raise BadRequestException("File has no extension. A valid file extension is required.")

        # Check dangerous extensions first
        if clean_ext in DANGEROUS_EXTENSIONS:
            raise BadRequestException(f"Files with extension '.{clean_ext}' are strictly prohibited.")

        # Check against allowed whitelist
        if clean_ext not in ALLOWED_EXTENSIONS:
            allowed_list = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise BadRequestException(
                f"File extension '.{clean_ext}' is not supported. Allowed formats: {allowed_list}"
            )

        # Sanitize original filename
        sanitized_filename = self._sanitize_original_filename(original_filename, clean_ext)

        # Validate MIME type
        expected_mime = MIME_TYPE_MAPPING.get(clean_ext)
        detected_mime = content_type or mimetypes.guess_type(sanitized_filename)[0] or expected_mime

        # Reject clearly dangerous content types
        if content_type and any(
            bad in content_type.lower()
            for bad in ["x-msdownload", "x-executable", "x-sh", "x-php", "javascript", "x-python"]
        ):
            raise BadRequestException("Dangerous content type detected.")

        return sanitized_filename, clean_ext, expected_mime or detected_mime

    def _save_file_to_disk(
        self,
        upload_file: UploadFile,
        clean_ext: str,
    ) -> Tuple[str, str, int]:
        """
        Streams uploaded file to disk with strict size enforcement and atomic cleanup.
        Returns tuple of (stored_filename, storage_path, file_size_bytes).
        """
        upload_dir = self._get_upload_dir()
        stored_filename = f"{uuid.uuid4().hex}.{clean_ext}"
        target_path = (upload_dir / stored_filename).resolve()

        # Path traversal prevention check
        if not str(target_path).startswith(str(upload_dir)):
            raise BadRequestException("Invalid storage destination.")

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        total_bytes = 0
        chunk_size = 64 * 1024  # 64 KB

        try:
            with open(target_path, "wb") as destination:
                while True:
                    chunk = upload_file.file.read(chunk_size)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        raise PayloadTooLargeException(
                            f"File size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB."
                        )
                    destination.write(chunk)

            if total_bytes == 0:
                raise BadRequestException("Uploaded file is empty (0 bytes).")

            return stored_filename, str(target_path), total_bytes

        except Exception:
            # Clean up partial physical file on any failure
            self._safe_unlink(str(target_path))
            raise

    def _safe_unlink(self, storage_path: str) -> None:
        """
        Safely attempts to delete physical file from disk.
        Ensures the path is strictly within UPLOAD_DIR and handles missing files gracefully.
        """
        try:
            path = Path(storage_path).resolve()
            upload_dir = Path(settings.UPLOAD_DIR).resolve()
            # Security boundary: only delete inside configured upload directory
            if upload_dir in path.parents or path == upload_dir:
                if path.is_file():
                    path.unlink(missing_ok=True)
            else:
                logger.warning(f"Prevented deletion attempt outside upload directory: {storage_path}")
        except Exception as err:
            logger.warning(f"Error during physical file cleanup ({storage_path}): {err}")

    def check_challenge_upload_access(self, db: Session, challenge: Challenge, current_user: User) -> None:
        """Verifies if current_user has permission to upload attachments to this challenge."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if challenge.submitted_by_user_id == current_user.id:
            return

        if challenge.submitted_by_organization_id:
            membership = organization_repository.get_membership(
                db, challenge.submitted_by_organization_id, current_user.id
            )
            if membership and membership.is_active:
                return

        raise ForbiddenException("You are not authorized to attach files to this challenge.")

    def check_challenge_access(self, db: Session, challenge: Challenge, current_user: User) -> None:
        """Verifies if current_user has permission to access/view attachments for this challenge."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if challenge.submitted_by_user_id == current_user.id:
            return

        if challenge.submitted_by_organization_id:
            membership = organization_repository.get_membership(
                db, challenge.submitted_by_organization_id, current_user.id
            )
            if membership and membership.is_active:
                return

        raise ForbiddenException("You are not authorized to access attachments for this challenge.")

    def check_attachment_delete_access(
        self, db: Session, attachment: Attachment, challenge: Challenge, current_user: User
    ) -> None:
        """Verifies if current_user has permission to delete this attachment."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if attachment.uploaded_by_user_id == current_user.id:
            return

        if challenge.submitted_by_user_id == current_user.id:
            return

        raise ForbiddenException("You are not authorized to delete this attachment.")

    def upload_attachment(
        self,
        db: Session,
        challenge_id: str,
        upload_file: UploadFile,
        current_user: User,
    ) -> Attachment:
        """
        Validates, saves, and creates database record for a new challenge attachment.
        Rolls back and deletes saved file if database insertion fails.
        """
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge with ID '{challenge_id}' not found.")

        # Check authorization
        self.check_challenge_upload_access(db, challenge, current_user)

        # Validate filename and type
        sanitized_filename, clean_ext, mime_type = self.validate_file_metadata(
            upload_file.filename, upload_file.content_type
        )

        # Save physical file to disk
        stored_filename, storage_path, file_size = self._save_file_to_disk(upload_file, clean_ext)

        # Create database entity
        attachment = Attachment(
            challenge_id=challenge_id,
            uploaded_by_user_id=current_user.id,
            original_filename=sanitized_filename,
            stored_filename=stored_filename,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size=file_size,
            file_extension=f".{clean_ext}",
        )

        try:
            db.add(attachment)
            db.commit()
            db.refresh(attachment)
            logger.info(
                f"Attachment [{attachment.id}] successfully stored for challenge [{challenge_id}] by user [{current_user.id}]."
            )
            return attachment
        except Exception as exc:
            db.rollback()
            # Clean up the orphaned physical file
            self._safe_unlink(storage_path)
            logger.exception(f"Failed to persist attachment record in database: {exc}")
            raise JanSetuException(
                message="Failed to save attachment metadata.",
                code="ATTACHMENT_DATABASE_ERROR",
                status_code=500,
            )

    def list_attachments(
        self,
        db: Session,
        challenge_id: str,
        current_user: User,
    ) -> List[Attachment]:
        """Lists all attachments for a challenge, enforcing caller authorization."""
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge with ID '{challenge_id}' not found.")

        # Check authorization
        self.check_challenge_access(db, challenge, current_user)

        return (
            db.query(Attachment)
            .filter(Attachment.challenge_id == challenge_id)
            .order_by(Attachment.created_at.desc())
            .all()
        )

    def get_attachment_for_download(
        self,
        db: Session,
        attachment_id: str,
        current_user: User,
    ) -> Attachment:
        """
        Retrieves attachment entity and verifies authorization and physical file existence
        before allowing download.
        """
        attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not attachment:
            raise NotFoundException(f"Attachment with ID '{attachment_id}' not found.")

        challenge = db.query(Challenge).filter(Challenge.id == attachment.challenge_id).first()
        if not challenge:
            raise NotFoundException("Associated challenge no longer exists.")

        # Check authorization (must be uploader, challenge owner, active org member, or admin)
        if (
            current_user.role != UserRole.PLATFORM_ADMIN
            and attachment.uploaded_by_user_id != current_user.id
            and challenge.submitted_by_user_id != current_user.id
        ):
            if challenge.submitted_by_organization_id:
                membership = organization_repository.get_membership(
                    db, challenge.submitted_by_organization_id, current_user.id
                )
                if not membership or not membership.is_active:
                    raise ForbiddenException("You are not authorized to access this attachment.")
            else:
                raise ForbiddenException("You are not authorized to access this attachment.")

        # Ensure physical file is present on disk
        target_path = Path(attachment.storage_path).resolve()
        if not target_path.is_file():
            logger.error(f"Physical file missing on disk for attachment [{attachment_id}]: {attachment.storage_path}")
            raise NotFoundException("Attachment file not found on storage.")

        return attachment

    def delete_attachment(
        self,
        db: Session,
        attachment_id: str,
        current_user: User,
    ) -> None:
        """
        Deletes attachment database record and removes physical file from disk.
        Gracefully handles missing physical files.
        """
        attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not attachment:
            raise NotFoundException(f"Attachment with ID '{attachment_id}' not found.")

        challenge = db.query(Challenge).filter(Challenge.id == attachment.challenge_id).first()
        if not challenge:
            raise NotFoundException("Associated challenge no longer exists.")

        # Check authorization
        self.check_attachment_delete_access(db, attachment, challenge, current_user)

        storage_path = attachment.storage_path

        # 1. Delete database record
        db.delete(attachment)
        db.commit()

        # 2. Delete physical file (gracefully handling errors or missing files)
        self._safe_unlink(storage_path)
        logger.info(f"Attachment [{attachment_id}] deleted successfully.")


attachment_service = AttachmentService()
