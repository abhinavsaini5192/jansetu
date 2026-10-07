"""
Department and Capability Management Service for JanSetu Platform.
Enforces institutional ownership boundaries (university admins can only manage
their own university's departments) and capabilities metadata normalization.
"""
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.capability import Capability
from app.models.department import Department
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.schemas.department import (
    CapabilityCreate,
    DepartmentCreate,
    DepartmentUpdate,
)
from app.services.audit_service import audit_service
from app.utils.constants import is_valid_domain
from app.utils.enums import (
    AuditAction,
    OrganizationMembershipRole,
    OrganizationType,
    UserRole,
)


class DepartmentService:
    """Service handling academic departments and capability competencies."""

    def verify_university_admin(self, db: Session, user: User, university_id: str) -> None:
        """Verifies that user is platform admin or admin/owner of the university."""
        if user.role == UserRole.PLATFORM_ADMIN:
            return

        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.user_id == user.id,
                OrganizationMembership.organization_id == university_id,
                OrganizationMembership.is_active == True,
            )
            .first()
        )
        if not membership or membership.membership_role not in (
            OrganizationMembershipRole.ADMIN,
            OrganizationMembershipRole.OWNER,
        ):
            raise ForbiddenException("You do not have administrative permissions for this university.")

    def list_university_departments(
        self,
        db: Session,
        university_id: str,
        current_user: Optional[User] = None,
    ) -> List[Department]:
        """Lists departments belonging to a specific university."""
        # Verify university exists
        uni = db.query(Organization).filter(
            Organization.id == university_id,
            Organization.organization_type == OrganizationType.UNIVERSITY,
        ).first()
        if not uni:
            raise NotFoundException(f"University '{university_id}' not found.")

        query = (
            db.query(Department)
            .options(joinedload(Department.capabilities))
            .filter(Department.organization_id == university_id)
        )
        # Non-admins only see active departments
        is_admin = False
        if current_user:
            try:
                self.verify_university_admin(db, current_user, university_id)
                is_admin = True
            except ForbiddenException:
                pass

        if not is_admin:
            query = query.filter(Department.is_active == True)

        return query.all()

    def get_department_by_id(
        self,
        db: Session,
        department_id: str,
        current_user: Optional[User] = None,
    ) -> Department:
        """Retrieves a department by ID with capabilities."""
        dept = (
            db.query(Department)
            .options(joinedload(Department.capabilities))
            .filter(Department.id == department_id)
            .first()
        )
        if not dept:
            raise NotFoundException(f"Department '{department_id}' not found.")
        return dept

    def create_department(
        self,
        db: Session,
        university_id: str,
        req: DepartmentCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Department:
        """Creates a department for the university, enforcing institutional ownership."""
        self.verify_university_admin(db, current_user, university_id)

        # Check university exists
        uni = db.query(Organization).filter(
            Organization.id == university_id,
            Organization.organization_type == OrganizationType.UNIVERSITY,
        ).first()
        if not uni:
            raise NotFoundException(f"University '{university_id}' not found.")

        # Check name uniqueness within the same university
        dup = (
            db.query(Department)
            .filter(
                Department.organization_id == university_id,
                func.lower(Department.name) == req.name.strip().lower(),
            )
            .first()
        )
        if dup:
            raise ConflictException(f"Department '{req.name.strip()}' already exists in this university.")

        dept = Department(
            organization_id=university_id,
            name=req.name.strip(),
            code=req.code.strip() if req.code else None,
            description=req.description,
            contact_email=req.contact_email,
            contact_phone=req.contact_phone,
            is_active=True,
        )

        if req.capability_ids:
            caps = db.query(Capability).filter(Capability.id.in_(req.capability_ids)).all()
            dept.capabilities.extend(caps)

        db.add(dept)
        db.commit()
        db.refresh(dept)

        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="department",
            entity_id=dept.id,
            description=f"Created department '{dept.name}' in university '{uni.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return dept

    def update_department(
        self,
        db: Session,
        department_id: str,
        req: DepartmentUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Department:
        """Updates department details, enforcing that caller belongs to the department's university."""
        dept = self.get_department_by_id(db, department_id, current_user)
        self.verify_university_admin(db, current_user, dept.organization_id)

        if req.name and req.name.strip().lower() != dept.name.lower():
            dup = (
                db.query(Department)
                .filter(
                    Department.organization_id == dept.organization_id,
                    func.lower(Department.name) == req.name.strip().lower(),
                    Department.id != department_id,
                )
                .first()
            )
            if dup:
                raise ConflictException(f"Department '{req.name.strip()}' already exists in this university.")
            dept.name = req.name.strip()

        if req.code is not None:
            dept.code = req.code.strip() if req.code else None
        if req.description is not None:
            dept.description = req.description
        if req.contact_email is not None:
            dept.contact_email = req.contact_email
        if req.contact_phone is not None:
            dept.contact_phone = req.contact_phone
        if req.is_active is not None:
            dept.is_active = req.is_active

        db.commit()
        db.refresh(dept)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="department",
            entity_id=dept.id,
            description=f"Updated department '{dept.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return dept

    def delete_department(
        self,
        db: Session,
        department_id: str,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Deletes a department, enforcing ownership."""
        dept = self.get_department_by_id(db, department_id, current_user)
        self.verify_university_admin(db, current_user, dept.organization_id)

        audit_service.log_event(
            db=db,
            action=AuditAction.DELETE,
            entity_type="department",
            entity_id=dept.id,
            description=f"Deleted department '{dept.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.delete(dept)
        db.commit()

    def create_capability(
        self,
        db: Session,
        req: CapabilityCreate,
        current_user: User,
    ) -> Capability:
        """Creates a standardized domain capability."""
        if not is_valid_domain(req.domain.value):
            raise BadRequestException(f"Invalid domain: {req.domain.value}")

        cap = Capability(
            name=req.name.strip(),
            description=req.description,
            domain=req.domain,
            keywords=req.keywords,
            is_active=True,
        )
        db.add(cap)
        db.commit()
        db.refresh(cap)
        return cap

    def link_capability(
        self,
        db: Session,
        department_id: str,
        capability_id: str,
        current_user: User,
    ) -> Department:
        """Links a capability to a department."""
        dept = self.get_department_by_id(db, department_id, current_user)
        self.verify_university_admin(db, current_user, dept.organization_id)

        cap = db.query(Capability).filter(Capability.id == capability_id).first()
        if not cap:
            raise NotFoundException(f"Capability '{capability_id}' not found.")

        if cap not in dept.capabilities:
            dept.capabilities.append(cap)
            db.commit()
            db.refresh(dept)

        return dept

    def unlink_capability(
        self,
        db: Session,
        department_id: str,
        capability_id: str,
        current_user: User,
    ) -> Department:
        """Unlinks a capability from a department."""
        dept = self.get_department_by_id(db, department_id, current_user)
        self.verify_university_admin(db, current_user, dept.organization_id)

        cap = db.query(Capability).filter(Capability.id == capability_id).first()
        if not cap:
            raise NotFoundException(f"Capability '{capability_id}' not found.")

        if cap in dept.capabilities:
            dept.capabilities.remove(cap)
            db.commit()
            db.refresh(dept)

        return dept


department_service = DepartmentService()
