from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.project_team_member import ProjectTeamMember
from app.models.user import User
from app.schemas.team import TeamCreate, TeamMemberAdd, TeamMemberResponse, TeamMemberUpdate, TeamResponse, TeamUpdate
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.services.project_activity_service import project_activity_service
from app.utils.enums import AuditAction, NotificationType, OrganizationMembershipRole, ProjectActivityType, TeamRole, UserRole


class TeamService:
    """
    Project Team Management Service.
    Handles multidisciplinary student, faculty, and researcher team formation and permissions.
    """

    def _verify_team_management_permission(
        self,
        db: Session,
        project: Project,
        current_user: User,
        team: Optional[ProjectTeam] = None,
    ) -> None:
        """
        Ensures user is authorized to manage the team:
        - Platform Admin
        - University Admin/Owner of the project's university
        - Team Lead of the specific team
        """
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        # University Admin
        uni_membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if uni_membership or current_user.role == UserRole.UNIVERSITY_ADMIN:
            return

        # Project Creator
        if project.created_by_user_id == current_user.id:
            return

        # Team Lead of the team
        if team:
            lead_member = (
                db.query(ProjectTeamMember)
                .filter(
                    ProjectTeamMember.team_id == team.id,
                    ProjectTeamMember.user_id == current_user.id,
                    ProjectTeamMember.role == TeamRole.TEAM_LEAD,
                    ProjectTeamMember.is_active == True,
                )
                .first()
            )
            if lead_member:
                return

        raise ForbiddenException("You do not have permission to manage this project's team.")

    def create_team(
        self,
        db: Session,
        project_id: str,
        req: TeamCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectTeam:
        """Creates a multidisciplinary project team and assigns the creator as team lead."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        self._verify_team_management_permission(db, project, current_user)

        team = ProjectTeam(
            project_id=project_id,
            name=req.name,
            description=req.description,
            created_by_user_id=current_user.id,
        )
        db.add(team)
        db.flush()

        # Add current user as initial Team Lead
        member = ProjectTeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role=TeamRole.TEAM_LEAD,
            joined_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(member)
        db.commit()
        db.refresh(team)

        # Audit log and Activity timeline
        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="project_team",
            entity_id=team.id,
            description=f"Created team '{team.name}' under project '{project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=project_id,
            activity_type=ProjectActivityType.TEAM_CREATED,
            title="Team Created",
            description=f"Project team '{team.name}' formed by {current_user.full_name}",
            actor_user_id=current_user.id,
            related_entity_type="project_team",
            related_entity_id=team.id,
        )

        return team

    def list_project_teams(self, db: Session, project_id: str, current_user: User) -> List[ProjectTeam]:
        """Lists teams associated with a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not project_activity_service.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to view this project's teams.")

        return (
            db.query(ProjectTeam)
            .options(joinedload(ProjectTeam.members).joinedload(ProjectTeamMember.user))
            .filter(ProjectTeam.project_id == project_id)
            .all()
        )

    def get_team(self, db: Session, team_id: str, current_user: User) -> ProjectTeam:
        """Retrieves a single team by ID."""
        team = (
            db.query(ProjectTeam)
            .options(joinedload(ProjectTeam.members).joinedload(ProjectTeamMember.user), joinedload(ProjectTeam.project))
            .filter(ProjectTeam.id == team_id)
            .first()
        )
        if not team:
            raise NotFoundException(f"Team '{team_id}' not found.")

        if not project_activity_service.check_project_access(db, team.project, current_user):
            raise ForbiddenException("You do not have permission to access this team.")

        return team

    def update_team(
        self,
        db: Session,
        team_id: str,
        req: TeamUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectTeam:
        """Updates team name or description."""
        team = self.get_team(db, team_id, current_user)
        self._verify_team_management_permission(db, team.project, current_user, team)

        if req.name is not None:
            team.name = req.name
        if req.description is not None:
            team.description = req.description

        team.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(team)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="project_team",
            entity_id=team.id,
            description=f"Updated team '{team.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return team

    def delete_team(
        self,
        db: Session,
        team_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Deletes a team."""
        team = self.get_team(db, team_id, current_user)
        self._verify_team_management_permission(db, team.project, current_user, team)

        db.delete(team)
        db.commit()

        audit_service.log_event(
            db=db,
            action=AuditAction.DELETE,
            entity_type="project_team",
            entity_id=team_id,
            description=f"Deleted team '{team.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def add_team_member(
        self,
        db: Session,
        team_id: str,
        req: TeamMemberAdd,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectTeamMember:
        """Adds an active user to the team roster."""
        team = self.get_team(db, team_id, current_user)
        self._verify_team_management_permission(db, team.project, current_user, team)

        # Verify candidate user exists
        candidate = db.query(User).filter(User.id == req.user_id).first()
        if not candidate:
            raise NotFoundException(f"User '{req.user_id}' not found.")

        # Institutional scoping: Ensure user belongs to the university
        if current_user.role != UserRole.PLATFORM_ADMIN:
            uni_mem = (
                db.query(OrganizationMembership)
                .filter(
                    OrganizationMembership.user_id == candidate.id,
                    OrganizationMembership.organization_id == team.project.university_id,
                    OrganizationMembership.is_active == True,
                )
                .first()
            )
            if not uni_mem and candidate.role not in (UserRole.PLATFORM_ADMIN, UserRole.DISTRICT_NODAL_OFFICER):
                raise BadRequestException(f"User '{candidate.email}' does not belong to university '{team.project.university.name}'.")

        # Duplicate check
        existing = (
            db.query(ProjectTeamMember)
            .filter(ProjectTeamMember.team_id == team_id, ProjectTeamMember.user_id == candidate.id)
            .first()
        )
        if existing and existing.is_active:
            raise ConflictException(f"User '{candidate.full_name}' is already an active member of this team.")

        if existing:
            existing.is_active = True
            existing.role = req.role
            existing.updated_at = datetime.now(timezone.utc)
            member = existing
        else:
            member = ProjectTeamMember(
                team_id=team_id,
                user_id=candidate.id,
                role=req.role,
                joined_at=datetime.now(timezone.utc),
                is_active=True,
            )
            db.add(member)

        db.commit()
        db.refresh(member)

        # Activity & Audit
        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="project_team_member",
            entity_id=member.id,
            description=f"Added '{candidate.full_name}' as {member.role.value} to team '{team.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=team.project_id,
            activity_type=ProjectActivityType.MEMBER_ADDED,
            title="Team Member Added",
            description=f"{candidate.full_name} joined '{team.name}' as {member.role.value}",
            actor_user_id=current_user.id,
            related_entity_type="project_team_member",
            related_entity_id=member.id,
        )

        # Notify candidate user
        notification_service.create_notification(
            db=db,
            recipient_user_id=candidate.id,
            notification_type=NotificationType.SYSTEM,
            title="Added to Project Team",
            message=f"You have been added to '{team.name}' for project '{team.project.title}' as {member.role.value}.",
            related_challenge_id=team.project.challenge_id,
        )

        return member

    def list_team_members(self, db: Session, team_id: str, current_user: User) -> List[ProjectTeamMember]:
        """Lists active members of a team."""
        team = self.get_team(db, team_id, current_user)
        return (
            db.query(ProjectTeamMember)
            .options(joinedload(ProjectTeamMember.user))
            .filter(ProjectTeamMember.team_id == team_id, ProjectTeamMember.is_active == True)
            .all()
        )

    def update_team_member(
        self,
        db: Session,
        team_id: str,
        member_id: str,
        req: TeamMemberUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectTeamMember:
        """Updates team member role or active state."""
        team = self.get_team(db, team_id, current_user)
        self._verify_team_management_permission(db, team.project, current_user, team)

        member = (
            db.query(ProjectTeamMember)
            .filter(ProjectTeamMember.id == member_id, ProjectTeamMember.team_id == team_id)
            .first()
        )
        if not member:
            raise NotFoundException(f"Team member '{member_id}' not found.")

        # Guard: Prevent removing or demoting final team lead without replacement
        if member.role == TeamRole.TEAM_LEAD and (
            (req.role and req.role != TeamRole.TEAM_LEAD) or req.is_active is False
        ):
            other_leads = (
                db.query(ProjectTeamMember)
                .filter(
                    ProjectTeamMember.team_id == team_id,
                    ProjectTeamMember.id != member.id,
                    ProjectTeamMember.role == TeamRole.TEAM_LEAD,
                    ProjectTeamMember.is_active == True,
                )
                .count()
            )
            if other_leads == 0:
                raise BadRequestException("Cannot demote or deactivate the final team lead without designating a replacement.")

        if req.role is not None:
            member.role = req.role
        if req.is_active is not None:
            member.is_active = req.is_active

        member.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(member)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="project_team_member",
            entity_id=member.id,
            description=f"Updated membership for user {member.user_id} in team '{team.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return member

    def remove_team_member(
        self,
        db: Session,
        team_id: str,
        member_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Removes a member from the team roster."""
        team = self.get_team(db, team_id, current_user)
        self._verify_team_management_permission(db, team.project, current_user, team)

        member = (
            db.query(ProjectTeamMember)
            .filter(ProjectTeamMember.id == member_id, ProjectTeamMember.team_id == team_id)
            .first()
        )
        if not member:
            raise NotFoundException(f"Team member '{member_id}' not found.")

        # Guard against removing final team lead
        if member.role == TeamRole.TEAM_LEAD and member.is_active:
            other_leads = (
                db.query(ProjectTeamMember)
                .filter(
                    ProjectTeamMember.team_id == team_id,
                    ProjectTeamMember.id != member.id,
                    ProjectTeamMember.role == TeamRole.TEAM_LEAD,
                    ProjectTeamMember.is_active == True,
                )
                .count()
            )
            if other_leads == 0:
                raise BadRequestException("Cannot remove the final team lead without designating a replacement.")

        member.is_active = False
        member.updated_at = datetime.now(timezone.utc)
        db.commit()

        audit_service.log_event(
            db=db,
            action=AuditAction.DELETE,
            entity_type="project_team_member",
            entity_id=member.id,
            description=f"Removed user {member.user_id} from team '{team.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=team.project_id,
            activity_type=ProjectActivityType.MEMBER_REMOVED,
            title="Team Member Removed",
            description=f"Member removed from team '{team.name}'",
            actor_user_id=current_user.id,
            related_entity_type="project_team_member",
            related_entity_id=member.id,
        )

    def serialize_member_response(self, member: ProjectTeamMember) -> TeamMemberResponse:
        """Serializes team member ORM object to TeamMemberResponse schema with user details."""
        user_name = member.user.full_name if member.user else None
        user_email = member.user.email if member.user else None
        return TeamMemberResponse(
            id=member.id,
            team_id=member.team_id,
            user_id=member.user_id,
            user_name=user_name,
            user_email=user_email,
            role=member.role,
            joined_at=member.joined_at,
            is_active=member.is_active,
            created_at=member.created_at,
            updated_at=member.updated_at,
        )

    def serialize_team_response(self, team: ProjectTeam) -> TeamResponse:
        """Serializes team ORM object to TeamResponse schema with members."""
        active_members = [
            self.serialize_member_response(m)
            for m in (team.members or [])
            if m.is_active
        ]
        return TeamResponse(
            id=team.id,
            project_id=team.project_id,
            name=team.name,
            description=team.description,
            created_by_user_id=team.created_by_user_id,
            created_at=team.created_at,
            updated_at=team.updated_at,
            members=active_members,
        )


team_service = TeamService()
