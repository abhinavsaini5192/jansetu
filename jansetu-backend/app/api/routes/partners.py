"""
Industry & CSR Partnerships Endpoints.
Phase 2.9: Corporate, CSR, and Startup collaboration, resource commitments, and sponsorships.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user_optional
from app.core.exceptions import NotFoundException
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse
from app.schemas.partner import (
    PartnerInviteRequest,
    PartnerResponse,
    PartnerResponseRequest,
    SupportOfferCreate,
    SupportOfferResponse,
    SupportOfferUpdate,
)
from app.services.partner_service import partner_service
from app.utils.enums import OrganizationType

router = APIRouter()


# ---------------------------------------------------------------------------
# Project-Scoped Partnership Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/projects/{project_id}/partners/invite",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite Industry or CSR Partner",
    description="Invites an external partner organization to join an active project workspace.",
)
def invite_partner(
    project_id: str,
    payload: PartnerInviteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PartnerResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    partner = partner_service.invite_partner(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_partner_response(partner)


@router.post(
    "/projects/{project_id}/partnerships",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    summary="Create Project Partnership (Alias)",
)
def create_partnership_alias(
    project_id: str,
    payload: PartnerInviteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PartnerResponse:
    return invite_partner(
        project_id=project_id,
        payload=payload,
        request=request,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/partners",
    response_model=List[PartnerResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Partners",
)
def list_project_partners(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[PartnerResponse]:
    partners = partner_service.list_project_partners(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return [partner_service.serialize_partner_response(p) for p in partners]


@router.get(
    "/organizations/{organization_id}/partnerships",
    response_model=List[PartnerResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Partnerships",
    description="Lists all projects where this organization is an invited or active partner.",
)
def list_organization_partnerships(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[PartnerResponse]:
    partners = partner_service.list_organization_partnerships(
        db=db,
        organization_id=organization_id,
        current_user=current_user,
    )
    return [partner_service.serialize_partner_response(p) for p in partners]


# ---------------------------------------------------------------------------
# Individual Partner Decisions
# ---------------------------------------------------------------------------

@router.post(
    "/project-partners/{partner_id}/accept",
    response_model=PartnerResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Partnership Invitation",
)
def accept_partnership(
    partner_id: str,
    payload: Optional[PartnerResponseRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PartnerResponse:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or PartnerResponseRequest(decision="accept")
    partner = partner_service.accept_partnership(
        db=db,
        partner_id=partner_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_partner_response(partner)


@router.post(
    "/project-partners/{partner_id}/decline",
    response_model=PartnerResponse,
    status_code=status.HTTP_200_OK,
    summary="Decline Partnership Invitation",
)
def decline_partnership(
    partner_id: str,
    payload: Optional[PartnerResponseRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PartnerResponse:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or PartnerResponseRequest(decision="decline")
    partner = partner_service.decline_partnership(
        db=db,
        partner_id=partner_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_partner_response(partner)


@router.post(
    "/project-partners/{partner_id}/cancel",
    response_model=PartnerResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Partnership",
)
def cancel_partnership(
    partner_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PartnerResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    partner = partner_service.cancel_partnership(
        db=db,
        partner_id=partner_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_partner_response(partner)


# ---------------------------------------------------------------------------
# Partner Support Offers
# ---------------------------------------------------------------------------

@router.post(
    "/project-partners/{partner_id}/support",
    response_model=SupportOfferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Resource Support Offer",
    description="Registers funding, hardware, lab access, or mentorship support.",
)
def add_support_offer(
    partner_id: str,
    payload: SupportOfferCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SupportOfferResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    support = partner_service.create_support_offer(
        db=db,
        partner_id=partner_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_support_response(support)


@router.get(
    "/project-partners/{partner_id}/support",
    response_model=List[SupportOfferResponse],
    status_code=status.HTTP_200_OK,
    summary="List Partner Support Offers",
)
def list_support_offers(
    partner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SupportOfferResponse]:
    offers = partner_service.list_support_offers(
        db=db,
        partner_id=partner_id,
        current_user=current_user,
    )
    return [partner_service.serialize_support_response(s) for s in offers]


@router.patch(
    "/partner-support/{support_id}",
    response_model=SupportOfferResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Support Offer",
)
def update_support_offer(
    support_id: str,
    payload: SupportOfferUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SupportOfferResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    support = partner_service.update_support_offer(
        db=db,
        support_id=support_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return partner_service.serialize_support_response(support)


# ---------------------------------------------------------------------------
# Industry Directory Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/industry/partners",
    response_model=List[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Industry & CSR Organizations",
    description="Retrieves active industry, CSR, startup, and NGO organizations available for partnership.",
)
def list_industry_organizations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> List[OrganizationResponse]:
    partner_types = [
        OrganizationType.INDUSTRY,
        OrganizationType.COMMUNITY,
        OrganizationType.NGO,
        OrganizationType.STARTUP,
        OrganizationType.RESEARCH_LAB,
    ]
    orgs = (
        db.query(Organization)
        .filter(Organization.organization_type.in_(partner_types), Organization.is_active == True)
        .order_by(Organization.name.asc())
        .all()
    )
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get(
    "/industry/partners/{id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Industry Partner Organization",
)
def get_industry_organization(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> OrganizationResponse:
    org = db.query(Organization).filter(Organization.id == id, Organization.is_active == True).first()
    if not org:
        raise NotFoundException(f"Partner organization '{id}' not found.")
    return OrganizationResponse.model_validate(org)
