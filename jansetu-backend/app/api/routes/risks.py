"""
Project Risks & Mitigation Endpoints.
Phase 2.10: Risk registration, deterministic scoring (severity * likelihood), and mitigation tracking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.risk import (
    RiskCreate,
    RiskResolveRequest,
    RiskResponse,
    RiskUpdate,
)
from app.services.risk_service import risk_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Project-Scoped Risk Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/projects/{project_id}/risks",
    response_model=RiskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Risk",
    description="Logs a project risk with deterministic score calculated from severity and likelihood.",
)
def create_risk(
    project_id: str,
    payload: RiskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    risk = risk_service.create_risk(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return RiskResponse.model_validate(risk)


@router.get(
    "/projects/{project_id}/risks",
    response_model=List[RiskResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Risks",
    description="Retrieves risks sorted by highest risk score first.",
)
def list_project_risks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[RiskResponse]:
    risks = risk_service.list_risks(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return [RiskResponse.model_validate(r) for r in risks]


# ---------------------------------------------------------------------------
# Individual Risk Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/risks/{risk_id}",
    response_model=RiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Risk Details",
)
def get_risk(
    risk_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskResponse:
    risk = risk_service.get_risk(
        db=db,
        risk_id=risk_id,
        current_user=current_user,
    )
    return RiskResponse.model_validate(risk)


@router.patch(
    "/risks/{risk_id}",
    response_model=RiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Risk",
    description="Updates risk mitigation plan, severity, likelihood, or assigned owner.",
)
def update_risk(
    risk_id: str,
    payload: RiskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    risk = risk_service.update_risk(
        db=db,
        risk_id=risk_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return RiskResponse.model_validate(risk)


@router.post(
    "/risks/{risk_id}/resolve",
    response_model=RiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Risk",
    description="Marks a risk as resolved with optional resolution notes.",
)
def resolve_risk(
    risk_id: str,
    payload: Optional[RiskResolveRequest] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RiskResponse:
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    req = payload or RiskResolveRequest()
    risk = risk_service.resolve_risk(
        db=db,
        risk_id=risk_id,
        req=req,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return RiskResponse.model_validate(risk)
