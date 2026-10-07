"""
Audit Log Service for JanSetu Platform.
Provides centralized logging of critical governance, security, and lifecycle events.
Ensures zero storage of passwords, tokens, or sensitive credentials.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException
from app.core.logging_config import logger
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.enums import AuditAction, UserRole

# Keys that must NEVER be logged into metadata
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "jwt",
    "authorization",
    "secret",
    "key",
    "credential",
}


class AuditService:
    """Service for creating and querying immutable audit trails."""

    def _sanitize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """Recursively sanitizes dictionary removing credentials/tokens before JSON serialization."""
        if not metadata or not isinstance(metadata, dict):
            return None

        clean_dict = {}
        for k, v in metadata.items():
            if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
                clean_dict[k] = "[REDACTED]"
            elif isinstance(v, dict):
                clean_dict[k] = json.loads(self._sanitize_metadata(v) or "{}")
            elif isinstance(v, (str, int, float, bool)) or v is None:
                clean_dict[k] = v
            else:
                clean_dict[k] = str(v)

        return json.dumps(clean_dict)

    def record_audit_event(
        self,
        db: Session,
        action: Union[AuditAction, str],
        entity_type: str,
        entity_id: str,
        description: str,
        actor: Optional[Union[User, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        actor_user_id: Optional[str] = None,
    ) -> AuditLog:
        """
        Persists an immutable audit log record.
        Actor can be a User object, a user UUID string, or None for system events.
        """
        actor_id: Optional[str] = None
        if actor_user_id:
            actor_id = actor_user_id
        elif isinstance(actor, User):
            actor_id = actor.id
        elif isinstance(actor, str):
            actor_id = actor

        action_str = action.value if isinstance(action, AuditAction) else str(action)
        safe_metadata_json = self._sanitize_metadata(metadata)

        audit_entry = AuditLog(
            actor_user_id=actor_id,
            action=action_str,
            entity_type=entity_type,
            entity_id=str(entity_id),
            description=description,
            metadata_json=safe_metadata_json,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else None,
        )

        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            return audit_entry
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to write audit log: {e}")
            # Audit failures must not break the primary user operation, but should be logged
            return audit_entry

    def list_audit_logs(
        self,
        db: Session,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Tuple[List[AuditLog], int, int]:
        """
        Lists audit records with filtering and pagination.
        Access restricted to PLATFORM_ADMIN and GOVERNMENT_ADMIN.
        """
        if current_user.role not in (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN):
            raise ForbiddenException("Access to audit logs is restricted to platform and government administrators.")

        query = select(AuditLog).options(joinedload(AuditLog.actor))

        if actor_id:
            query = query.where(AuditLog.actor_user_id == actor_id)
        if action:
            query = query.where(AuditLog.action == action.lower())
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type.lower())
        if from_date:
            query = query.where(AuditLog.created_at >= from_date)
        if to_date:
            query = query.where(AuditLog.created_at <= to_date)

        # Count total
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        # Pagination
        skip = (page - 1) * page_size
        stmt = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(page_size)
        items = list(db.scalars(stmt).all())

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return items, total, total_pages

    log_event = record_audit_event


audit_service = AuditService()
