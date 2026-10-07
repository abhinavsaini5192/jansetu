"""
Organization and Membership Management Endpoints.
Handles institutional registration, profile discovery, updates, and membership RBAC.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    require_authenticated_user,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationMembershipCreateRequest,
    OrganizationMembershipResponse,
    OrganizationMembershipUpdateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.services.organization_service import organization_service
from app.utils.enums import OrganizationType

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organizations",
    description="Lists organizations with optional filtering by type, district, status, or search keywords.",
)
def list_organizations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[OrganizationType] = Query(None, description="Filter by organization type"),
    organization_type: Optional[OrganizationType] = Query(None, description="Alias for type"),
    district: Optional[str] = Query(None, description="Filter by Jharkhand district"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Keyword search across name and description"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[OrganizationResponse]:
    """Retrieve paginated list of organizations."""
    effective_type = type or organization_type
    items, total, total_pages = organization_service.list_organizations(
        db=db,
        page=page,
        page_size=page_size,
        organization_type=effective_type,
        district=district,
        is_active=is_active,
        search=search,
    )
    serialized_items = [OrganizationResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        success=True,
        data=serialized_items,
        items=serialized_items,
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
    description="Registers a new institutional entity. Enforces role-based institutional permissions.",
)
def create_organization(
    payload: OrganizationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> OrganizationResponse:
    """Create a new organization and assign caller as OWNER."""
    org = organization_service.create_organization(db, payload, current_user)
    return OrganizationResponse.model_validate(org)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Organization Details",
    description="Retrieves public profile for a specific organization.",
)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    """Fetch organization by primary ID."""
    org = organization_service.get_organization(db, organization_id)
    return OrganizationResponse.model_validate(org)


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Organization",
    description="Updates organization metadata. Restricted to organization OWNER/ADMIN or platform admin.",
)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> OrganizationResponse:
    """Update organization profile."""
    updated = organization_service.update_organization(db, organization_id, payload, current_user)
    return OrganizationResponse.model_validate(updated)


@router.get(
    "/{organization_id}/members",
    response_model=List[OrganizationMembershipResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Members",
    description="Lists all affiliated members for an organization.",
)
def list_members(
    organization_id: str,
    is_active: Optional[bool] = Query(None, description="Filter active/inactive memberships"),
    db: Session = Depends(get_db),
) -> List[OrganizationMembershipResponse]:
    """List members belonging to the specified organization."""
    members = organization_service.list_members(db, organization_id, is_active=is_active)
    return [OrganizationMembershipResponse.model_validate(m) for m in members]


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Organization Member",
    description="Enrolls an existing user as an organization member. Requires OWNER/ADMIN or platform admin.",
)
def add_member(
    organization_id: str,
    payload: OrganizationMembershipCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> OrganizationMembershipResponse:
    """Add a member to an organization."""
    membership = organization_service.add_member(db, organization_id, payload, current_user)
    return OrganizationMembershipResponse.model_validate(membership)


@router.patch(
    "/{organization_id}/members/{user_id}",
    response_model=OrganizationMembershipResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Member Role or Status",
    description="Modifies a member's institutional role or activates/deactivates membership.",
)
def update_member(
    organization_id: str,
    user_id: str,
    payload: OrganizationMembershipUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> OrganizationMembershipResponse:
    """Update membership role or active state."""
    membership = organization_service.update_member(db, organization_id, user_id, payload, current_user)
    return OrganizationMembershipResponse.model_validate(membership)


@router.delete(
    "/{organization_id}/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove Organization Member",
    description="Removes a member from the organization. Cannot remove the sole owner.",
)
def remove_member(
    organization_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Remove a membership association."""
    organization_service.remove_member(db, organization_id, user_id, current_user)
    return {"success": True, "message": "Member removed successfully"}
