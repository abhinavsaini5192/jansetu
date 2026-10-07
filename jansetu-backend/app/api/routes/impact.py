"""
Impact Management and Evidence Verification API Routes (Phases 3.6 & 3.7).
Endpoints for post-completion impact outcomes, evidence submission, and state verification.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user_optional
from app.models.challenge import Challenge
from app.models.project import Project
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.impact import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceVerificationRequest,
    ImpactCreate,
    ImpactResponse,
    ImpactUpdate,
    ImpactVerificationRequest,
)
from app.services.impact_service import impact_service

router = APIRouter()


# ==============================================================================
# PROJECT IMPACT ROUTES
# ==============================================================================

@router.post(
    "/projects/{project_id}/impact",
    response_model=ApiResponse[ImpactResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Impact Assessment",
)
def create_project_impact(
    project_id: str,
    payload: ImpactCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[ImpactResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    record = impact_service.create_impact(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Impact assessment created successfully.",
        data=impact_service.serialize_impact_response(record),
    )


@router.get(
    "/projects/{project_id}/impact",
    response_model=Optional[ImpactResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Project Impact Assessment",
)
def get_project_impact(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Optional[ImpactResponse]:
    record = impact_service.get_impact_by_project_id(db, project_id)
    if not record:
        return None
    return impact_service.serialize_impact_response(record)


# ==============================================================================
# FRONTEND CHALLENGE COMPATIBILITY ROUTES (Screen 09)
# ==============================================================================

@router.get(
    "/challenges/{challenge_id}/impact",
    response_model=Optional[ImpactResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Impact for Challenge (Frontend Alias)",
)
def get_challenge_impact(
    challenge_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Optional[ImpactResponse]:
    record = impact_service.get_impact_by_challenge_id(db, challenge_id)
    if not record:
        return None
    return impact_service.serialize_impact_response(record)


@router.post(
    "/challenges/{challenge_id}/impact/evidence",
    response_model=ApiResponse[ImpactResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit Impact Evidence for Challenge (Frontend Alias)",
)
def submit_challenge_impact_evidence(
    challenge_id: str,
    payload: ImpactCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[ImpactResponse]:
    """Frontend Screen 09 compatibility: handles both impact baseline/outcome data and evidence."""
    # Find existing impact or create one
    record = impact_service.get_impact_by_challenge_id(db, challenge_id)
    if not record:
        project = db.query(Project).filter(Project.challenge_id == challenge_id).first()
        if not project:
            # Create a placeholder project if missing so challenge has a valid workspace
            challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
            project = Project(
                challenge_id=challenge_id,
                organization_id=challenge.submitted_by_organization_id if challenge and challenge.submitted_by_organization_id else None,
                lead_user_id=current_user.id,
                title=f"Project for {challenge.title if challenge else 'Challenge'}",
            )
            db.add(project)
            db.flush()

        record = impact_service.create_impact(db=db, project_id=project.id, req=payload, current_user=current_user)
    else:
        # Update existing record with submitted values
        update_req = ImpactUpdate(
            villages_covered=payload.villages_covered or payload.villagesCovered,
            actual_beneficiaries=payload.actual_beneficiaries or payload.beneficiariesReached,
            baseline_value=payload.baseline_value or payload.baselineMetric,
            achieved_value=payload.achieved_value or payload.postInterventionMetric,
            economic_benefit=payload.economic_benefit or payload.economicBenefit,
        )
        record = impact_service.update_impact(db, record.id, update_req, current_user)

    return ApiResponse(
        success=True,
        message="Field impact evidence submitted successfully.",
        data=impact_service.serialize_impact_response(record),
    )


# ==============================================================================
# INDIVIDUAL IMPACT ITEM OPERATIONS
# ==============================================================================

@router.get(
    "/impact/{impact_id}",
    response_model=ImpactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Impact Record by ID",
)
def get_impact_detail(
    impact_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ImpactResponse:
    record = impact_service.get_impact_by_id(db, impact_id)
    return impact_service.serialize_impact_response(record)


@router.patch(
    "/impact/{impact_id}",
    response_model=ImpactResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Draft Impact Record",
)
def update_impact_record(
    impact_id: str,
    payload: ImpactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ImpactResponse:
    record = impact_service.update_impact(db, impact_id, payload, current_user)
    return impact_service.serialize_impact_response(record)


@router.post(
    "/impact/{impact_id}/submit",
    response_model=ImpactResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Impact for Verification",
)
def submit_impact_record(
    impact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ImpactResponse:
    record = impact_service.submit_impact(db, impact_id, current_user)
    return impact_service.serialize_impact_response(record)


@router.post(
    "/impact/{impact_id}/verify",
    response_model=ApiResponse[ImpactResponse],
    status_code=status.HTTP_200_OK,
    summary="Authorize Government Verification",
)
def verify_impact_record(
    impact_id: str,
    payload: ImpactVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[ImpactResponse]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    record = impact_service.verify_impact(
        db=db,
        impact_id=impact_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ApiResponse(
        success=True,
        message="Government verification stamp executed successfully.",
        data=impact_service.serialize_impact_response(record),
    )


@router.post(
    "/impact/{impact_id}/reject",
    response_model=ApiResponse[ImpactResponse],
    status_code=status.HTTP_200_OK,
    summary="Reject Impact Assessment",
)
def reject_impact_record(
    impact_id: str,
    payload: ImpactVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[ImpactResponse]:
    payload.decision = "REJECTED"
    record = impact_service.verify_impact(db=db, impact_id=impact_id, req=payload, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Impact assessment rejected.",
        data=impact_service.serialize_impact_response(record),
    )


@router.post(
    "/impact/{impact_id}/request-clarification",
    response_model=ApiResponse[ImpactResponse],
    status_code=status.HTTP_200_OK,
    summary="Request Clarification on Impact Assessment",
)
def request_impact_clarification(
    impact_id: str,
    payload: ImpactVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[ImpactResponse]:
    payload.decision = "NEEDS_CLARIFICATION"
    record = impact_service.verify_impact(db=db, impact_id=impact_id, req=payload, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Clarification requested on impact assessment.",
        data=impact_service.serialize_impact_response(record),
    )


# ==============================================================================
# EVIDENCE ATTACHMENT OPERATIONS (Phase 3.7)
# ==============================================================================

@router.post(
    "/impact/{impact_id}/evidence",
    response_model=ApiResponse[EvidenceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Attach Evidence Artifact to Impact Record",
)
def add_impact_evidence(
    impact_id: str,
    payload: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[EvidenceResponse]:
    evidence = impact_service.add_evidence(db, impact_id, payload, current_user)
    return ApiResponse(
        success=True,
        message="Evidence artifact attached.",
        data=impact_service.serialize_evidence_response(evidence),
    )


@router.get(
    "/impact/{impact_id}/evidence",
    response_model=ApiResponse[List[EvidenceResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Evidence Artifacts for Impact Record",
)
def list_impact_evidence(
    impact_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ApiResponse[List[EvidenceResponse]]:
    impact = impact_service.get_impact_by_id(db, impact_id)
    return ApiResponse(
        success=True,
        data=[impact_service.serialize_evidence_response(e) for e in impact.evidence_records],
    )


@router.get(
    "/evidence/{evidence_id}",
    response_model=EvidenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Evidence Artifact Detail",
)
def get_evidence_detail(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> EvidenceResponse:
    from app.models.evidence_record import EvidenceRecord
    ev = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
    if not ev:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Evidence artifact '{evidence_id}' not found.")
    return impact_service.serialize_evidence_response(ev)


@router.post(
    "/evidence/{evidence_id}/verify",
    response_model=ApiResponse[EvidenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Verify Evidence Artifact",
)
def verify_evidence_artifact(
    evidence_id: str,
    payload: EvidenceVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[EvidenceResponse]:
    payload.decision = "VERIFIED"
    ev = impact_service.verify_evidence(db, evidence_id, payload, current_user)
    return ApiResponse(
        success=True,
        message="Evidence artifact verified.",
        data=impact_service.serialize_evidence_response(ev),
    )


@router.post(
    "/evidence/{evidence_id}/reject",
    response_model=ApiResponse[EvidenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Reject Evidence Artifact",
)
def reject_evidence_artifact(
    evidence_id: str,
    payload: EvidenceVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[EvidenceResponse]:
    payload.decision = "REJECTED"
    ev = impact_service.verify_evidence(db, evidence_id, payload, current_user)
    return ApiResponse(
        success=True,
        message="Evidence artifact rejected.",
        data=impact_service.serialize_evidence_response(ev),
    )


@router.post(
    "/evidence/{evidence_id}/request-clarification",
    response_model=ApiResponse[EvidenceResponse],
    status_code=status.HTTP_200_OK,
    summary="Request Clarification on Evidence Artifact",
)
def clarify_evidence_artifact(
    evidence_id: str,
    payload: EvidenceVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[EvidenceResponse]:
    payload.decision = "NEEDS_CLARIFICATION"
    ev = impact_service.verify_evidence(db, evidence_id, payload, current_user)
    return ApiResponse(
        success=True,
        message="Clarification requested on evidence artifact.",
        data=impact_service.serialize_evidence_response(ev),
    )
