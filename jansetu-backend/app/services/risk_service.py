from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.project import Project
from app.models.project_risk import ProjectRisk, calculate_risk_score
from app.models.user import User
from app.schemas.risk import RiskCreate, RiskResolveRequest, RiskUpdate
from app.services.audit_service import audit_service
from app.services.project_activity_service import project_activity_service
from app.utils.enums import AuditAction, ProjectActivityType, RiskStatus, UserRole


class RiskService:
    """
    Project Risk Tracking & Mitigation Service.
    Maintains transparent, deterministic risk calculations based on severity and likelihood.
    """

    def _verify_risk_editor(self, db: Session, project: Project, current_user: User) -> None:
        """Verifies authorized project participant who can edit/resolve risks."""
        if current_user.role in (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER):
            return

        if project.created_by_user_id == current_user.id:
            return

        # University Member
        from app.models.organization_membership import OrganizationMembership
        uni_membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if uni_membership:
            return

        # Project Team Member
        from app.models.project_team import ProjectTeam
        from app.models.project_team_member import ProjectTeamMember
        team_m = (
            db.query(ProjectTeamMember)
            .join(ProjectTeam, ProjectTeam.id == ProjectTeamMember.team_id)
            .filter(
                ProjectTeam.project_id == project.id,
                ProjectTeamMember.user_id == current_user.id,
                ProjectTeamMember.is_active == True,
            )
            .first()
        )
        if team_m:
            return

        # Partner Member
        from app.models.project_partner import ProjectPartner
        from app.utils.enums import PartnerStatus
        partner_m = (
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
        if partner_m:
            return

        raise ForbiddenException("You do not have permission to manage risks for this project.")

    def create_risk(
        self,
        db: Session,
        project_id: str,
        req: RiskCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectRisk:
        """Creates a project risk with deterministic score calculation."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        self._verify_risk_editor(db, project, current_user)

        score = calculate_risk_score(req.severity, req.likelihood)

        risk = ProjectRisk(
            project_id=project_id,
            title=req.title,
            description=req.description,
            severity=req.severity,
            likelihood=req.likelihood,
            risk_score=score,
            mitigation_plan=req.mitigation_plan,
            owner_user_id=req.owner_user_id,
            status=RiskStatus.OPEN,
            identified_by_user_id=current_user.id,
        )
        db.add(risk)
        db.commit()
        db.refresh(risk)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="project_risk",
            entity_id=risk.id,
            description=f"Identified risk '{risk.title}' (Score: {risk.risk_score})",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=project_id,
            activity_type=ProjectActivityType.RISK_CREATED,
            title="Risk Flagged",
            description=f"Risk '{risk.title}' (Score: {risk.risk_score}, Severity: {risk.severity.value})",
            actor_user_id=current_user.id,
            related_entity_type="project_risk",
            related_entity_id=risk.id,
        )

        return risk

    def list_risks(self, db: Session, project_id: str, current_user: User) -> List[ProjectRisk]:
        """Lists risks for a project ordered highest risk score first."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not project_activity_service.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to view this project's risks.")

        return (
            db.query(ProjectRisk)
            .filter(ProjectRisk.project_id == project_id)
            .order_by(desc(ProjectRisk.risk_score), desc(ProjectRisk.created_at))
            .all()
        )

    def get_risk(self, db: Session, risk_id: str, current_user: User) -> ProjectRisk:
        """Retrieves a single risk by ID."""
        risk = (
            db.query(ProjectRisk)
            .options(joinedload(ProjectRisk.project), joinedload(ProjectRisk.owner_user))
            .filter(ProjectRisk.id == risk_id)
            .first()
        )
        if not risk:
            raise NotFoundException(f"Project risk '{risk_id}' not found.")

        if not project_activity_service.check_project_access(db, risk.project, current_user):
            raise ForbiddenException("You do not have permission to access this risk.")

        return risk

    def update_risk(
        self,
        db: Session,
        risk_id: str,
        req: RiskUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectRisk:
        """Updates a risk and recalculates risk score if severity/likelihood changed."""
        risk = self.get_risk(db, risk_id, current_user)
        self._verify_risk_editor(db, risk.project, current_user)

        if req.title is not None:
            risk.title = req.title
        if req.description is not None:
            risk.description = req.description
        if req.severity is not None:
            risk.severity = req.severity
        if req.likelihood is not None:
            risk.likelihood = req.likelihood
        if req.mitigation_plan is not None:
            risk.mitigation_plan = req.mitigation_plan
        if req.owner_user_id is not None:
            risk.owner_user_id = req.owner_user_id
        if req.status is not None:
            risk.status = req.status
            if req.status == RiskStatus.RESOLVED and not risk.resolved_at:
                risk.resolved_at = datetime.now(timezone.utc)

        risk.risk_score = calculate_risk_score(risk.severity, risk.likelihood)
        risk.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(risk)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="project_risk",
            entity_id=risk.id,
            description=f"Updated risk '{risk.title}' (Score: {risk.risk_score}, Status: {risk.status.value})",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=risk.project_id,
            activity_type=ProjectActivityType.RISK_UPDATED,
            title="Risk Updated",
            description=f"Risk '{risk.title}' updated (Status: {risk.status.value})",
            actor_user_id=current_user.id,
            related_entity_type="project_risk",
            related_entity_id=risk.id,
        )

        return risk

    def resolve_risk(
        self,
        db: Session,
        risk_id: str,
        req: RiskResolveRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectRisk:
        """Resolves a project risk."""
        risk = self.get_risk(db, risk_id, current_user)
        self._verify_risk_editor(db, risk.project, current_user)

        risk.status = RiskStatus.RESOLVED
        risk.resolved_at = datetime.now(timezone.utc)
        if req.resolution_notes:
            existing_notes = f"\nResolution: {req.resolution_notes}" if risk.mitigation_plan else f"Resolution: {req.resolution_notes}"
            risk.mitigation_plan = (risk.mitigation_plan or "") + existing_notes

        risk.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(risk)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="project_risk",
            entity_id=risk.id,
            description=f"Resolved risk '{risk.title}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=risk.project_id,
            activity_type=ProjectActivityType.STATUS_CHANGED,
            title="Risk Resolved",
            description=f"Risk '{risk.title}' marked as resolved",
            actor_user_id=current_user.id,
            related_entity_type="project_risk",
            related_entity_id=risk.id,
        )

        return risk


risk_service = RiskService()
