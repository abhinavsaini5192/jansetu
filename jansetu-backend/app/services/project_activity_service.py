import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.logging_config import logger
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.project import Project
from app.models.project_activity import ProjectActivity
from app.models.project_partner import ProjectPartner
from app.models.user import User
from app.utils.enums import OrganizationMembershipRole, PartnerStatus, ProjectActivityType, UserRole


class ProjectActivityService:
    """
    Project Activity Timeline & Auditing Service.
    Automatically records milestone, proposal, team, risk, and partner events.
    """

    def record_activity(
        self,
        db: Session,
        project_id: str,
        activity_type: Union[ProjectActivityType, str],
        title: str,
        description: Optional[str] = None,
        actor_user_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        metadata_dict: Optional[dict] = None,
    ) -> ProjectActivity:
        """
        Records an auditable project activity entry.
        Does not crash the enclosing transaction if recording fails.
        """
        type_str = activity_type.value if isinstance(activity_type, ProjectActivityType) else str(activity_type)
        meta_json = json.dumps(metadata_dict) if metadata_dict else None

        activity = ProjectActivity(
            project_id=project_id,
            actor_user_id=actor_user_id,
            activity_type=type_str,
            title=title,
            description=description,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            metadata_json=meta_json,
        )
        try:
            db.add(activity)
            db.flush()
            return activity
        except Exception as e:
            logger.warning(f"Failed to record project activity for project {project_id}: {e}")
            return activity

    def check_project_access(self, db: Session, project: Project, current_user: User) -> bool:
        """
        Verifies if current_user is authorized to view private project data.
        """
        # Platform Admin and Government roles have oversight
        if current_user.role in (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER):
            return True

        # Challenge Submitter or Project Creator
        if project.created_by_user_id == current_user.id:
            return True
        if project.challenge and project.challenge.submitted_by_user_id == current_user.id:
            return True

        # University Member
        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if membership:
            return True

        # Check if user is a member of an accepted partner organization
        partner_member = (
            db.query(ProjectPartner)
            .join(OrganizationMembership, OrganizationMembership.organization_id == ProjectPartner.organization_id)
            .filter(
                ProjectPartner.project_id == project.id,
                ProjectPartner.status.in_([PartnerStatus.ACCEPTED, PartnerStatus.ACTIVE]),
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if partner_member:
            return True

        return False

    def list_project_timeline(
        self,
        db: Session,
        project_id: str,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        activity_type: Optional[str] = None,
    ) -> Tuple[List[ProjectActivity], int, int]:
        """
        Retrieves paginated project activities ordered newest first.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not self.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to access this project's timeline.")

        query = (
            db.query(ProjectActivity)
            .options(joinedload(ProjectActivity.actor_user))
            .filter(ProjectActivity.project_id == project_id)
        )

        if activity_type:
            query = query.filter(ProjectActivity.activity_type == activity_type)

        total_items = query.count()
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        offset = (page - 1) * page_size

        activities = (
            query.order_by(desc(ProjectActivity.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return activities, total_items, total_pages


project_activity_service = ProjectActivityService()
