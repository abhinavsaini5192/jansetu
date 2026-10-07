"""
Solution Proposals Endpoints.
Phase 2.7: Institutional solution proposal submission, revision requests, and administrative review.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.proposal import (
    ProposalCreate,
    ProposalHistoryItem,
    ProposalResponse,
    ProposalReviewRequest,
    ProposalUpdate,
)
from app.services.proposal_service import proposal_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Project-Scoped Proposal Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/projects/{project_id}/proposals",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Solution Proposal Draft",
    description="Drafts an institutional solution blueprint for an assigned project.",
)
def create_proposal(
    project_id: str,
    payload: ProposalCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProposalResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    proposal = proposal_service.create_proposal(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ProposalResponse.model_validate(proposal)


@router.get(
    "/projects/{project_id}/proposals",
    response_model=List[ProposalResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Proposals",
)
def list_project_proposals(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ProposalResponse]:
    proposals = proposal_service.list_proposals(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return [ProposalResponse.model_validate(p) for p in proposals]


# ---------------------------------------------------------------------------
# Individual Proposal Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/proposals/{proposal_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Proposal Details",
)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProposalResponse:
    proposal = proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        current_user=current_user,
    )
    return ProposalResponse.model_validate(proposal)


@router.patch(
    "/proposals/{proposal_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Proposal",
    description="Updates draft proposal or addresses revision remarks.",
)
def update_proposal(
    proposal_id: str,
    payload: ProposalUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProposalResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    proposal = proposal_service.update_proposal(
        db=db,
        proposal_id=proposal_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ProposalResponse.model_validate(proposal)


@router.post(
    "/proposals/{proposal_id}/submit",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Proposal for Official Review",
    description="Transitions proposal from DRAFT/NEEDS_REVISION to SUBMITTED.",
)
def submit_proposal(
    proposal_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProposalResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    proposal = proposal_service.submit_proposal(
        db=db,
        proposal_id=proposal_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ProposalResponse.model_validate(proposal)


@router.post(
    "/proposals/{proposal_id}/review",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Review Proposal",
    description="Government or platform authority approves, rejects, or requests revisions for a solution proposal.",
)
def review_proposal(
    proposal_id: str,
    payload: ProposalReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProposalResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    proposal = proposal_service.review_proposal(
        db=db,
        proposal_id=proposal_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return ProposalResponse.model_validate(proposal)


@router.get(
    "/proposals/{proposal_id}/history",
    response_model=List[ProposalHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get Proposal Review History",
    description="Returns chronological audit trail of changes and review decisions for the proposal.",
)
def get_proposal_history(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ProposalHistoryItem]:
    return proposal_service.get_proposal_history(
        db=db,
        proposal_id=proposal_id,
        current_user=current_user,
    )
