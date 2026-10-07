"""
Project Teams & Member Roster Endpoints.
Phase 2.6: Multidisciplinary team formation, student/faculty assignments, and roster management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamMemberAdd,
    TeamMemberResponse,
    TeamMemberUpdate,
    TeamResponse,
    TeamUpdate,
)
from app.services.team_service import team_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Project-Scoped Team Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/projects/{project_id}/teams",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project Team",
    description="Forms a multidisciplinary project team for an institutional project workspace.",
)
def create_team(
    project_id: str,
    payload: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    team = team_service.create_team(
        db=db,
        project_id=project_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return team_service.serialize_team_response(team)


@router.post(
    "/projects/{project_id}/team",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    summary="Create Project Team (Alias)",
)
def create_team_alias(
    project_id: str,
    payload: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamResponse:
    return create_team(
        project_id=project_id,
        payload=payload,
        request=request,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/teams",
    response_model=List[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Teams",
    description="Retrieves all active multidisciplinary teams under a project workspace.",
)
def list_project_teams(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[TeamResponse]:
    teams = team_service.list_project_teams(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return [team_service.serialize_team_response(t) for t in teams]


# ---------------------------------------------------------------------------
# Individual Team Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/teams/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Team Details",
)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamResponse:
    team = team_service.get_team(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )
    return team_service.serialize_team_response(team)


@router.patch(
    "/teams/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Team",
)
def update_team(
    team_id: str,
    payload: TeamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    team = team_service.update_team(
        db=db,
        team_id=team_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return team_service.serialize_team_response(team)


@router.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Team",
)
def delete_team(
    team_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    team_service.delete_team(
        db=db,
        team_id=team_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Team Member Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/teams/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Team Member",
    description="Adds a university student, faculty mentor, or researcher to the team roster.",
)
def add_team_member(
    team_id: str,
    payload: TeamMemberAdd,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamMemberResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    member = team_service.add_team_member(
        db=db,
        team_id=team_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return team_service.serialize_member_response(member)


@router.get(
    "/teams/{team_id}/members",
    response_model=List[TeamMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List Team Members",
)
def list_team_members(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[TeamMemberResponse]:
    members = team_service.list_team_members(
        db=db,
        team_id=team_id,
        current_user=current_user,
    )
    return [team_service.serialize_member_response(m) for m in members]


@router.patch(
    "/teams/{team_id}/members/{member_id}",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Team Member Role",
)
def update_team_member(
    team_id: str,
    member_id: str,
    payload: TeamMemberUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TeamMemberResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    member = team_service.update_team_member(
        db=db,
        team_id=team_id,
        member_id=member_id,
        req=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return team_service.serialize_member_response(member)


@router.delete(
    "/teams/{team_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Team Member",
)
def remove_team_member(
    team_id: str,
    member_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    team_service.remove_team_member(
        db=db,
        team_id=team_id,
        member_id=member_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
