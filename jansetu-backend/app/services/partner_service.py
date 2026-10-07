from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.partner_support import PartnerSupport
from app.models.project import Project
from app.models.project_partner import ProjectPartner
from app.models.user import User
from app.schemas.partner import (
    PartnerInviteRequest,
    PartnerResponse,
    PartnerResponseRequest,
    SupportOfferCreate,
    SupportOfferResponse,
    SupportOfferUpdate,
)
from app.services.audit_service import audit_service
from app.services.notification_service import notification_service
from app.services.project_activity_service import project_activity_service
from app.utils.enums import (
    AuditAction,
    NotificationType,
    OrganizationMembershipRole,
    OrganizationType,
    PartnerStatus,
    PartnerType,
    ProjectActivityType,
    SupportStatus,
    SupportType,
    UserRole,
)


class PartnerService:
    """
    Industry & CSR Collaboration Service.
    Coordinates public-private-academic alliances, corporate sponsorship, and support commitments.
    """

    def _verify_project_inviter(self, db: Session, project: Project, current_user: User) -> None:
        """Ensures user can invite partners (Government, University Admin, or Platform Admin)."""
        allowed_roles = (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER)
        if current_user.role in allowed_roles:
            return

        if project.created_by_user_id == current_user.id:
            return

        uni_m = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == project.university_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if uni_m or current_user.role == UserRole.UNIVERSITY_ADMIN:
            return

        raise ForbiddenException("Only university or government project authorities can invite external partners.")

    def _verify_partner_admin(self, db: Session, organization_id: str, current_user: User) -> None:
        """Ensures user is an authorized administrator of the partner organization."""
        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        mem = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if not mem:
            raise ForbiddenException("You must be an administrator of the partner organization to respond to invitations.")

    def invite_partner(
        self,
        db: Session,
        project_id: str,
        req: PartnerInviteRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectPartner:
        """Invites a corporate, CSR, startup, or NGO partner to support a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        self._verify_project_inviter(db, project, current_user)

        target_org_id = req.organization_id or req.partner_id or req.partnerId
        if not target_org_id:
            raise BadRequestException("Target organization_id (or partner_id) is required.")

        partner_org = db.query(Organization).filter(Organization.id == target_org_id).first()
        if not partner_org:
            raise NotFoundException(f"Organization '{target_org_id}' not found.")

        if target_org_id == project.university_id:
            raise BadRequestException("A university cannot invite itself as an external partner.")

        # Check for duplicate active partnership
        existing = (
            db.query(ProjectPartner)
            .filter(
                ProjectPartner.project_id == project_id,
                ProjectPartner.organization_id == target_org_id,
                ProjectPartner.status.in_([PartnerStatus.INVITED, PartnerStatus.ACCEPTED, PartnerStatus.ACTIVE]),
            )
            .first()
        )
        if existing:
            raise ConflictException(f"An active partnership with '{partner_org.name}' already exists (Status: {existing.status.value}).")

        # Map partner type
        if req.partner_type:
            p_type = req.partner_type
        elif partner_org.organization_type == OrganizationType.STARTUP:
            p_type = PartnerType.STARTUP
        elif partner_org.organization_type == OrganizationType.NGO:
            p_type = PartnerType.NGO
        else:
            p_type = PartnerType.INDUSTRY

        partner = ProjectPartner(
            project_id=project_id,
            organization_id=target_org_id,
            partner_type=p_type,
            status=PartnerStatus.INVITED,
            invited_by_user_id=current_user.id,
            invitation_message=req.invitation_message or f"Invitation to collaborate on project {project.project_code}",
        )
        db.add(partner)
        db.flush()

        # If frontend provided supportType string, record an initial support offer
        supp_text = req.supportType or req.support_type
        if supp_text:
            support = PartnerSupport(
                project_partner_id=partner.id,
                support_type=SupportType.FUNDING,
                description=f"Initial support package: {supp_text}",
                status=SupportStatus.PROPOSED,
            )
            db.add(support)

        db.commit()
        db.refresh(partner)

        # Activity & Audit
        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="project_partner",
            entity_id=partner.id,
            description=f"Invited '{partner_org.name}' to project '{project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=project_id,
            activity_type=ProjectActivityType.PARTNER_INVITED,
            title="Partner Invited",
            description=f"Invitation sent to {partner_org.name} ({p_type.value.upper()})",
            actor_user_id=current_user.id,
            related_entity_type="project_partner",
            related_entity_id=partner.id,
        )

        # Notify partner organization admins
        partner_admins = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == target_org_id,
                OrganizationMembership.membership_role.in_([OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER]),
                OrganizationMembership.is_active == True,
            )
            .all()
        )
        for admin_m in partner_admins:
            notification_service.create_notification(
                db=db,
                recipient_user_id=admin_m.user_id,
                notification_type=NotificationType.SYSTEM,
                title="Project Partnership Invitation",
                message=f"Your organization '{partner_org.name}' has been invited to collaborate on '{project.title}'.",
                related_challenge_id=project.challenge_id,
            )

        return partner

    def list_project_partners(self, db: Session, project_id: str, current_user: User) -> List[ProjectPartner]:
        """Lists all partners associated with a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        if not project_activity_service.check_project_access(db, project, current_user):
            raise ForbiddenException("You do not have permission to view this project's partners.")

        return (
            db.query(ProjectPartner)
            .options(joinedload(ProjectPartner.organization), joinedload(ProjectPartner.support_offers))
            .filter(ProjectPartner.project_id == project_id)
            .all()
        )

    def list_organization_partnerships(self, db: Session, organization_id: str, current_user: User) -> List[ProjectPartner]:
        """Lists all projects that a specific organization is partnered with."""
        return (
            db.query(ProjectPartner)
            .options(joinedload(ProjectPartner.project), joinedload(ProjectPartner.organization))
            .filter(ProjectPartner.organization_id == organization_id)
            .all()
        )

    def get_partner(self, db: Session, partner_id: str, current_user: User) -> ProjectPartner:
        """Retrieves a single project partner record."""
        partner = (
            db.query(ProjectPartner)
            .options(joinedload(ProjectPartner.project), joinedload(ProjectPartner.organization), joinedload(ProjectPartner.support_offers))
            .filter(ProjectPartner.id == partner_id)
            .first()
        )
        if not partner:
            raise NotFoundException(f"Project partner '{partner_id}' not found.")

        return partner

    def accept_partnership(
        self,
        db: Session,
        partner_id: str,
        req: PartnerResponseRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectPartner:
        """Accepts an invitation to join the project."""
        partner = self.get_partner(db, partner_id, current_user)
        self._verify_partner_admin(db, partner.organization_id, current_user)

        if partner.status != PartnerStatus.INVITED:
            raise BadRequestException(f"Cannot accept partnership in '{partner.status.value}' status.")

        partner.status = PartnerStatus.ACCEPTED
        partner.joined_at = datetime.now(timezone.utc)
        if req.response_message:
            partner.response_message = req.response_message
        partner.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(partner)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="project_partner",
            entity_id=partner.id,
            description=f"Partner '{partner.organization.name}' accepted partnership for '{partner.project.project_code}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=partner.project_id,
            activity_type=ProjectActivityType.PARTNER_ACCEPTED,
            title="Partnership Formed",
            description=f"{partner.organization.name} joined as active partner",
            actor_user_id=current_user.id,
            related_entity_type="project_partner",
            related_entity_id=partner.id,
        )

        return partner

    def decline_partnership(
        self,
        db: Session,
        partner_id: str,
        req: PartnerResponseRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectPartner:
        """Declines an invitation."""
        partner = self.get_partner(db, partner_id, current_user)
        self._verify_partner_admin(db, partner.organization_id, current_user)

        if partner.status != PartnerStatus.INVITED:
            raise BadRequestException(f"Cannot decline partnership in '{partner.status.value}' status.")

        partner.status = PartnerStatus.DECLINED
        if req.response_message:
            partner.response_message = req.response_message
        partner.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(partner)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="project_partner",
            entity_id=partner.id,
            description=f"Partner '{partner.organization.name}' declined partnership",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return partner

    def cancel_partnership(
        self,
        db: Session,
        partner_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProjectPartner:
        """Cancels a partnership (by project or government admin)."""
        partner = self.get_partner(db, partner_id, current_user)
        self._verify_project_inviter(db, partner.project, current_user)

        partner.status = PartnerStatus.CANCELLED
        partner.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(partner)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="project_partner",
            entity_id=partner.id,
            description=f"Cancelled partnership for '{partner.organization.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return partner

    def create_support_offer(
        self,
        db: Session,
        partner_id: str,
        req: SupportOfferCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PartnerSupport:
        """Adds a support offer (funding estimate, equipment, mentor)."""
        partner = self.get_partner(db, partner_id, current_user)
        self._verify_partner_admin(db, partner.organization_id, current_user)

        support = PartnerSupport(
            project_partner_id=partner_id,
            support_type=req.support_type,
            description=req.description,
            estimated_value=req.estimated_value,
            status=SupportStatus.PROPOSED,
        )
        db.add(support)
        db.commit()
        db.refresh(support)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="partner_support",
            entity_id=support.id,
            description=f"Added support offer ({support.support_type.value}): {support.description[:50]}",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        project_activity_service.record_activity(
            db=db,
            project_id=partner.project_id,
            activity_type=ProjectActivityType.SUPPORT_ADDED,
            title="Resource Support Proposed",
            description=f"{partner.organization.name} offered {support.support_type.value}: {support.description[:60]}",
            actor_user_id=current_user.id,
            related_entity_type="partner_support",
            related_entity_id=support.id,
        )

        return support

    add_support_offer = create_support_offer

    def list_support_offers(self, db: Session, partner_id: str, current_user: User) -> List[PartnerSupport]:
        """Lists support offers for a partner."""
        partner = self.get_partner(db, partner_id, current_user)
        return db.query(PartnerSupport).filter(PartnerSupport.project_partner_id == partner_id).all()

    def update_support_offer(
        self,
        db: Session,
        support_id: str,
        req: SupportOfferUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PartnerSupport:
        """Updates a support offer."""
        support = (
            db.query(PartnerSupport)
            .options(joinedload(PartnerSupport.partner))
            .filter(PartnerSupport.id == support_id)
            .first()
        )
        if not support:
            raise NotFoundException(f"Partner support '{support_id}' not found.")

        # Partner admin can update their own offer
        self._verify_partner_admin(db, support.partner.organization_id, current_user)

        if req.support_type is not None:
            support.support_type = req.support_type
        if req.description is not None:
            support.description = req.description
        if req.estimated_value is not None:
            support.estimated_value = req.estimated_value
        if req.status is not None:
            support.status = req.status

        support.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(support)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="partner_support",
            entity_id=support.id,
            description=f"Updated partner support offer {support.id}",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return support

    def serialize_support_response(self, support: PartnerSupport) -> SupportOfferResponse:
        """Serializes PartnerSupport ORM model to SupportOfferResponse schema."""
        return SupportOfferResponse(
            id=support.id,
            project_partner_id=support.project_partner_id,
            support_type=support.support_type,
            description=support.description,
            estimated_value=support.estimated_value,
            status=support.status,
            created_at=support.created_at,
            updated_at=support.updated_at,
        )

    def serialize_partner_response(self, partner: ProjectPartner) -> PartnerResponse:
        """Serializes ProjectPartner ORM model to PartnerResponse schema including org name and support offers."""
        org_name = partner.organization.name if partner.organization else None
        offers = [self.serialize_support_response(s) for s in (partner.support_offers or [])]
        return PartnerResponse(
            id=partner.id,
            project_id=partner.project_id,
            organization_id=partner.organization_id,
            organization_name=org_name,
            partner_type=partner.partner_type,
            status=partner.status,
            invited_by_user_id=partner.invited_by_user_id,
            invitation_message=partner.invitation_message,
            response_message=partner.response_message,
            joined_at=partner.joined_at,
            created_at=partner.created_at,
            updated_at=partner.updated_at,
            support_offers=offers,
        )


partner_service = PartnerService()
