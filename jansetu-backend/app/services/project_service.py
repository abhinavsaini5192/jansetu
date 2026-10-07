"""
Project Workspace Service for JanSetu Platform.
Manages the lifecycle of collaborative university project workspaces initialized
from accepted challenge mandates, ensuring idempotent creation, strict RBAC, and audit trails.
"""
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.challenge import Challenge
from app.models.challenge_assignment import ChallengeAssignment
from app.models.department import Department
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.utils.enums import (
    AuditAction,
    NotificationType,
    OrganizationMembershipRole,
    OrganizationType,
    ProjectStatus,
    UserRole,
)


class ProjectService:
    """Service handling project workspace creation, roster management, and execution monitoring."""

    def verify_project_access(self, db: Session, user: User, project: Project) -> None:
        """
        Enforces project visibility:
        - Platform admins and government reviewers can view any project.
        - University members can view their own university's projects.
        - The challenge's original submitter can view the project workspace.
        """
        if user.role in (
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_ADMIN,
            UserRole.DISTRICT_NODAL_OFFICER,
        ):
            return

        if project.challenge and project.challenge.submitted_by_user_id == user.id:
            return

        # Check university membership
        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if membership:
            return

        raise ForbiddenException("You do not have permission to access this project workspace.")

    def verify_project_management(self, db: Session, user: User, project: Project) -> None:
        """Verifies that user is platform admin or admin/lead of the project's university."""
        if user.role == UserRole.PLATFORM_ADMIN:
            return

        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if not membership or membership.membership_role not in (
            OrganizationMembershipRole.ADMIN,
            OrganizationMembershipRole.OWNER,
            OrganizationMembershipRole.MEMBER,
        ):
            raise ForbiddenException("You do not have management permissions for this project.")

    def get_or_create_project_for_assignment(
        self,
        db: Session,
        assignment: ChallengeAssignment,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Project:
        """
        Idempotently creates a Project workspace for an accepted ChallengeAssignment.
        If a workspace already exists for this assignment or challenge-university pairing, returns it.
        """
        existing = (
            db.query(Project)
            .filter(
                (Project.assignment_id == assignment.id) |
                ((Project.challenge_id == assignment.challenge_id) & (Project.university_id == assignment.university_id))
            )
            .first()
        )
        if existing:
            return existing

        challenge = db.query(Challenge).filter(Challenge.id == assignment.challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{assignment.challenge_id}' not found.")

        dept_name = assignment.department.name if assignment.department else "Interdisciplinary Technical Pool"

        project = Project(
            challenge_id=assignment.challenge_id,
            assignment_id=assignment.id,
            university_id=assignment.university_id,
            department_id=assignment.department_id,
            title=f"Project: {challenge.title}",
            description=f"Institutional execution workspace for mandate '{challenge.reference_code}'. Sub-department: {dept_name}.",
            status=ProjectStatus.ACTIVE,
            created_by_user_id=current_user.id,
            lead_faculty="Faculty Mentor Appointed",
            student_lead="Multidisciplinary Student Lead",
            budget="Under Institutional Review",
            progress_percentage=0,
        )
        db.add(project)
        db.flush()

        # Emit audit log
        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="project",
            entity_id=project.id,
            description=f"Initialized project workspace '{project.project_code}' for challenge '{challenge.reference_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Notify challenge submitter
        notification_service.create_notification(
            db=db,
            recipient_user_id=challenge.submitted_by_user_id,
            notification_type=NotificationType.SYSTEM,
            title="Project Workspace Created",
            message=f"An institutional project workspace ({project.project_code}) has been created for your challenge '{challenge.title}'.",
            related_challenge_id=challenge.id,
        )

        return project

    def create_project(
        self,
        db: Session,
        req: ProjectCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Project:
        """Handles manual project proposal creation as invoked by the frontend workspace modal."""
        if not req.challenge_id:
            raise BadRequestException("challenge_id is required to create a project workspace.")

        challenge = db.query(Challenge).filter(Challenge.id == req.challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{req.challenge_id}' not found.")

        # Resolve university ID
        university_id = req.university_id
        if not university_id and req.institutionName:
            org = db.query(Organization).filter(
                Organization.organization_type == OrganizationType.UNIVERSITY,
                func.lower(Organization.name) == req.institutionName.strip().lower(),
            ).first()
            if org:
                university_id = org.id

        if not university_id:
            # Fallback to current user's university membership
            membership = (
                db.query(OrganizationMembership)
                .join(Organization)
                .filter(
                    OrganizationMembership.user_id == current_user.id,
                    Organization.organization_type == OrganizationType.UNIVERSITY,
                    OrganizationMembership.is_active == True,
                )
                .first()
            )
            if membership:
                university_id = membership.organization_id

        if not university_id:
            raise BadRequestException("Valid university_id or accredited institution name is required.")

        # Idempotency check
        existing = (
            db.query(Project)
            .filter(Project.challenge_id == challenge.id, Project.university_id == university_id)
            .first()
        )
        if existing:
            return existing

        project = Project(
            challenge_id=challenge.id,
            university_id=university_id,
            department_id=req.department_id,
            title=req.title or f"Project: {challenge.title}",
            description=req.description or challenge.description,
            status=ProjectStatus.ACTIVE,
            created_by_user_id=current_user.id,
            lead_faculty=req.lead_faculty or "Dr. Assigned Faculty",
            student_lead=req.student_lead or "Appointed Student Lead",
            budget=req.budget or "₹50,000 (Seed)",
            progress_percentage=0,
            start_date=req.start_date,
            target_completion_date=req.target_completion_date,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="project",
            entity_id=project.id,
            description=f"Created project proposal '{project.title}' ({project.project_code})",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return project

    def get_project_by_id(
        self,
        db: Session,
        project_id: str,
        current_user: Optional[User] = None,
    ) -> Project:
        """Retrieves a project workspace by ID, enforcing RBAC."""
        project = (
            db.query(Project)
            .options(
                joinedload(Project.challenge),
                joinedload(Project.university),
                joinedload(Project.department),
            )
            .filter(Project.id == project_id)
            .first()
        )
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if current_user:
            self.verify_project_access(db, current_user, project)

        return project

    def get_project_by_challenge_id(
        self,
        db: Session,
        challenge_id: str,
        current_user: Optional[User] = None,
    ) -> Project:
        """Retrieves project workspace associated with a challenge."""
        project = (
            db.query(Project)
            .options(
                joinedload(Project.challenge),
                joinedload(Project.university),
                joinedload(Project.department),
            )
            .filter(Project.challenge_id == challenge_id)
            .first()
        )
        if not project:
            raise NotFoundException(f"No active project workspace found for challenge '{challenge_id}'.")

        if current_user:
            self.verify_project_access(db, current_user, project)

        return project

    def list_projects(
        self,
        db: Session,
        university_id: Optional[str] = None,
        challenge_id: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        page: int = 1,
        page_size: int = 20,
        current_user: Optional[User] = None,
    ) -> Tuple[List[Project], int, int]:
        """Lists projects with filtering and pagination."""
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        query = (
            select(Project)
            .options(
                joinedload(Project.challenge),
                joinedload(Project.university),
                joinedload(Project.department),
            )
        )

        if university_id:
            query = query.where(Project.university_id == university_id)
        if challenge_id:
            query = query.where(Project.challenge_id == challenge_id)
        if status:
            query = query.where(Project.status == status)

        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        skip = (page - 1) * page_size
        stmt = query.order_by(desc(Project.created_at)).offset(skip).limit(page_size)
        items = list(db.scalars(stmt).unique().all())

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return items, total, total_pages

    def update_project(
        self,
        db: Session,
        project_id: str,
        req: ProjectUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Project:
        """Updates project details, milestones progress, or status."""
        project = self.get_project_by_id(db, project_id, current_user)
        self.verify_project_management(db, current_user, project)

        if req.title is not None:
            project.title = req.title.strip()
        if req.description is not None:
            project.description = req.description
        if req.status is not None:
            project.status = req.status
        if req.lead_faculty is not None:
            project.lead_faculty = req.lead_faculty
        if req.student_lead is not None:
            project.student_lead = req.student_lead
        if req.budget is not None:
            project.budget = req.budget
        if req.progress_percentage is not None:
            project.progress_percentage = req.progress_percentage
        if req.start_date is not None:
            project.start_date = req.start_date
        if req.target_completion_date is not None:
            project.target_completion_date = req.target_completion_date

        db.commit()
        db.refresh(project)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="project",
            entity_id=project.id,
            description=f"Updated project workspace '{project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return project

    def serialize_project_response(self, project: Project) -> ProjectResponse:
        """Populates backend and frontend-compatible fields for ProjectResponse."""
        institution_name = project.university.name if project.university else "Lead University"
        dept_name = project.department.name if project.department else "Multidisciplinary Engineering"

        # Check actual database team members, milestones, and risks
        actual_members = []
        for t in (project.teams or []):
            for m in (t.members or []):
                if m.is_active:
                    actual_members.append({
                        "id": m.id,
                        "name": m.user.full_name if m.user else "Team Member",
                        "role": m.role.value,
                        "dept": dept_name,
                        "email": m.user.email if m.user else None,
                    })
        team_members = actual_members

        actual_milestones = []
        for m in (project.milestones or []):
            actual_milestones.append({
                "id": m.id,
                "title": m.title,
                "status": m.status.value,
                "dueDate": m.planned_end_date.strftime("%Y-%m-%d") if m.planned_end_date else None,
                "progress": m.completion_percentage,
            })
        milestones = actual_milestones

        actual_risks = []
        for r in (project.risks or []):
            actual_risks.append({
                "id": r.id,
                "title": r.title,
                "severity": r.severity.value,
                "status": r.status.value,
                "score": r.risk_score,
            })
        risks = actual_risks

        prop_summary = project.description
        if project.proposals:
            latest_prop = sorted(project.proposals, key=lambda p: p.created_at, reverse=True)[0]
            prop_summary = latest_prop.summary or project.description

        return ProjectResponse(
            id=project.id,
            project_code=project.project_code,
            challenge_id=project.challenge_id,
            assignment_id=project.assignment_id,
            university_id=project.university_id,
            department_id=project.department_id,
            title=project.title,
            description=project.description,
            status=project.status,
            created_by_user_id=project.created_by_user_id,
            lead_faculty=project.lead_faculty,
            student_lead=project.student_lead,
            budget=project.budget,
            progress_percentage=project.progress_percentage,
            start_date=project.start_date,
            target_completion_date=project.target_completion_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
            # Frontend camelCase
            code=project.project_code,
            name=project.title,
            institutionName=institution_name,
            department=dept_name,
            progressPercentage=project.progress_percentage,
            leadFaculty=project.lead_faculty,
            studentLead=project.student_lead,
            currentStage=project.status.value.replace("_", " ").title(),
            proposalSummary=prop_summary,
            teamMembers=team_members,
            milestones=milestones,
            risks=actual_risks,
        )


project_service = ProjectService()
