"""
Audit Log Management API Routes.
Provides restricted endpoints for compliance, security auditing, and tracking governance decisions.
Restricted to PLATFORM_ADMIN and GOVERNMENT_ADMIN roles.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse
from app.services.audit_service import audit_service

router = APIRouter()


@router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Audit Logs",
    description="Retrieves immutable system audit records. Restricted to Platform and Government Admins.",
)
def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Frontend alias for page_size"),
    actor: Optional[str] = Query(None, description="Filter by actor user ID"),
    actor_id: Optional[str] = Query(None, description="Alternative alias for actor user ID"),
    action: Optional[str] = Query(None, description="Filter by audit action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (challenge, attachment, etc.)"),
    from_date: Optional[datetime] = Query(None, description="Filter records created on or after this timestamp"),
    to_date: Optional[datetime] = Query(None, description="Filter records created on or before this timestamp"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> AuditLogListResponse:
    """Query audit logs with authorization checks and comprehensive filtering."""
    effective_limit = limit or page_size or 20
    effective_actor = actor_id or actor

    items, total, total_pages = audit_service.list_audit_logs(
        db=db,
        current_user=current_user,
        page=page,
        page_size=effective_limit,
        actor_id=effective_actor,
        action=action,
        entity_type=entity_type,
        from_date=from_date,
        to_date=to_date,
    )

    serialized = [AuditLogResponse.model_validate(item) for item in items]
    return AuditLogListResponse(
        items=serialized,
        total=total,
        page=page,
        page_size=effective_limit,
        total_pages=total_pages,
    )
