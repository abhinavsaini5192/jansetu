"""
University Directory Service for JanSetu Platform.
Manages Higher Education Institution (HEI) representations using the Organization
and UniversityProfile models with strict verification controls and audit logging.
"""
from typing import List, Optional, Tuple
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.university_profile import UniversityProfile
from app.models.user import User
from app.schemas.university import (
    UniversityCreate,
    UniversityUpdate,
    UniversityVerificationUpdate,
)
from app.services.audit_service import audit_service
from app.utils.enums import (
    AuditAction,
    InstitutionCategory,
    OrganizationMembershipRole,
    OrganizationType,
    UserRole,
)


class UniversityService:
    """Service handling business domain logic for universities and institutional profiles."""

    @staticmethod
    def _is_privileged_admin(user: Optional[User]) -> bool:
        if not user:
            return False
        return user.role in (
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_ADMIN,
            UserRole.DISTRICT_NODAL_OFFICER,
        )

    def _check_university_admin_permission(self, db: Session, user: User, university_id: str) -> None:
        """Verifies that the user is a platform admin or an admin/owner of the university organization."""
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

    def list_universities(
        self,
        db: Session,
        search: Optional[str] = None,
        district: Optional[str] = None,
        category: Optional[InstitutionCategory] = None,
        is_verified: Optional[bool] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        current_user: Optional[User] = None,
    ) -> Tuple[List[Organization], int, int]:
        """
        Lists universities with search, filtering, and pagination.
        Public/unprivileged callers are restricted to active and verified universities by default.
        """
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        query = (
            select(Organization)
            .outerjoin(UniversityProfile, Organization.id == UniversityProfile.organization_id)
            .options(joinedload(Organization.university_profile))
            .where(Organization.organization_type == OrganizationType.UNIVERSITY)
        )

        privileged = self._is_privileged_admin(current_user)

        # Enforce visibility rules for public/unprivileged callers
        if not privileged:
            query = query.where(Organization.is_active == True)
            query = query.where(Organization.is_verified == True)
        else:
            if is_active is not None:
                query = query.where(Organization.is_active == is_active)
            if is_verified is not None:
                query = query.where(Organization.is_verified == is_verified)

        if district and district.strip():
            d_clean = district.strip().lower()
            query = query.where(func.lower(Organization.district) == d_clean)

        if category is not None:
            query = query.where(UniversityProfile.institution_category == category)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Organization.name).like(term),
                    func.lower(Organization.description).like(term),
                    func.lower(UniversityProfile.institution_code).like(term),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        # Paginate
        skip = (page - 1) * page_size
        stmt = query.order_by(desc(Organization.created_at)).offset(skip).limit(page_size)
        items = list(db.scalars(stmt).unique().all())

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return items, total, total_pages

    def get_university_by_id(
        self,
        db: Session,
        university_id: str,
        current_user: Optional[User] = None,
    ) -> Organization:
        """Retrieves a university by ID, verifying access rules."""
        university = (
            db.query(Organization)
            .options(
                joinedload(Organization.university_profile),
                joinedload(Organization.departments),
            )
            .filter(
                Organization.id == university_id,
                Organization.organization_type == OrganizationType.UNIVERSITY,
            )
            .first()
        )
        if not university:
            raise NotFoundException(f"University '{university_id}' not found.")

        # If not active or not verified, only privileged users or university admins can view
        if not (university.is_active and university.is_verified):
            if not self._is_privileged_admin(current_user):
                if not current_user:
                    raise NotFoundException(f"University '{university_id}' not found.")
                self._check_university_admin_permission(db, current_user, university_id)

        return university

    def create_university(
        self,
        db: Session,
        req: UniversityCreate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        """Creates a university organization and associated profile."""
        if current_user.role not in (
            UserRole.PLATFORM_ADMIN,
            UserRole.GOVERNMENT_ADMIN,
            UserRole.DISTRICT_NODAL_OFFICER,
            UserRole.UNIVERSITY_ADMIN,
        ):
            raise ForbiddenException("Citizens cannot create universities.")

        # Check unique organization name
        existing = db.query(Organization).filter(func.lower(Organization.name) == req.name.strip().lower()).first()
        if existing:
            raise ConflictException(f"Organization with name '{req.name.strip()}' already exists.")

        # Verification rule: Only PLATFORM_ADMIN can create directly pre-verified universities
        is_verified = (current_user.role == UserRole.PLATFORM_ADMIN)

        org = Organization(
            name=req.name.strip(),
            legal_name=req.legal_name.strip() if req.legal_name else None,
            organization_type=OrganizationType.UNIVERSITY,
            description=req.description,
            email=req.email,
            phone=req.phone,
            website=req.website,
            address=req.address,
            district=req.district,
            state=req.state or "Jharkhand",
            is_active=True,
            is_verified=is_verified,
        )
        db.add(org)
        db.flush()

        # Build Profile
        prof_data = req.profile
        profile = UniversityProfile(
            organization_id=org.id,
            institution_code=prof_data.institution_code if prof_data else None,
            institution_category=prof_data.institution_category if prof_data else InstitutionCategory.UNIVERSITY,
            accreditation_details=prof_data.accreditation_details if prof_data else None,
            established_year=prof_data.established_year if prof_data else None,
            official_contact_email=prof_data.official_contact_email if prof_data else req.email,
            official_website=prof_data.official_website if prof_data else req.website,
            description=prof_data.description if prof_data else req.description,
            address=prof_data.address if prof_data else req.address,
            district=prof_data.district if prof_data else req.district,
            state=prof_data.state if prof_data else org.state,
            pincode=prof_data.pincode if prof_data else None,
            latitude=prof_data.latitude if prof_data else None,
            longitude=prof_data.longitude if prof_data else None,
            is_verified=is_verified,
            is_active=True,
        )
        db.add(profile)

        # Grant creator ownership membership if university admin
        membership = OrganizationMembership(
            user_id=current_user.id,
            organization_id=org.id,
            membership_role=OrganizationMembershipRole.OWNER,
            is_active=True,
        )
        db.add(membership)
        db.commit()
        db.refresh(org)

        # Audit Log
        audit_service.log_event(
            db=db,
            action=AuditAction.CREATE,
            entity_type="university",
            entity_id=org.id,
            description=f"Created university '{org.name}' (verified={is_verified})",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return org

    def update_university(
        self,
        db: Session,
        university_id: str,
        req: UniversityUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        """Updates university metadata. Prevents non-privileged users from changing verification."""
        self._check_university_admin_permission(db, current_user, university_id)
        university = self.get_university_by_id(db, university_id, current_user)

        if req.name and req.name.strip().lower() != university.name.lower():
            dup = db.query(Organization).filter(func.lower(Organization.name) == req.name.strip().lower()).first()
            if dup and dup.id != university_id:
                raise ConflictException(f"Organization with name '{req.name.strip()}' already exists.")
            university.name = req.name.strip()

        if req.legal_name is not None:
            university.legal_name = req.legal_name.strip() if req.legal_name else None
        if req.description is not None:
            university.description = req.description
        if req.email is not None:
            university.email = req.email
        if req.phone is not None:
            university.phone = req.phone
        if req.website is not None:
            university.website = req.website
        if req.address is not None:
            university.address = req.address
        if req.district is not None:
            university.district = req.district
        if req.state is not None:
            university.state = req.state
        if req.is_active is not None and current_user.role == UserRole.PLATFORM_ADMIN:
            university.is_active = req.is_active

        # Update profile if provided
        if req.profile:
            p_data = req.profile
            prof = university.university_profile
            if not prof:
                prof = UniversityProfile(organization_id=university.id)
                db.add(prof)

            if p_data.institution_code is not None:
                prof.institution_code = p_data.institution_code
            if p_data.institution_category is not None:
                prof.institution_category = p_data.institution_category
            if p_data.accreditation_details is not None:
                prof.accreditation_details = p_data.accreditation_details
            if p_data.established_year is not None:
                prof.established_year = p_data.established_year
            if p_data.official_contact_email is not None:
                prof.official_contact_email = p_data.official_contact_email
            if p_data.official_website is not None:
                prof.official_website = p_data.official_website
            if p_data.description is not None:
                prof.description = p_data.description
            if p_data.address is not None:
                prof.address = p_data.address
            if p_data.district is not None:
                prof.district = p_data.district
            if p_data.state is not None:
                prof.state = p_data.state
            if p_data.pincode is not None:
                prof.pincode = p_data.pincode
            if p_data.latitude is not None:
                prof.latitude = p_data.latitude
            if p_data.longitude is not None:
                prof.longitude = p_data.longitude
            if p_data.is_active is not None and current_user.role == UserRole.PLATFORM_ADMIN:
                prof.is_active = p_data.is_active

        db.commit()
        db.refresh(university)

        audit_service.log_event(
            db=db,
            action=AuditAction.UPDATE,
            entity_type="university",
            entity_id=university.id,
            description=f"Updated university '{university.name}'",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return university

    def verify_university(
        self,
        db: Session,
        university_id: str,
        verify_req: UniversityVerificationUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        """Sets verification status. Only platform admin or authorized government admin can call this."""
        if not self._is_privileged_admin(current_user):
            raise ForbiddenException("Only platform or government administrators can verify universities.")

        university = (
            db.query(Organization)
            .filter(
                Organization.id == university_id,
                Organization.organization_type == OrganizationType.UNIVERSITY,
            )
            .first()
        )
        if not university:
            raise NotFoundException(f"University '{university_id}' not found.")

        university.is_verified = verify_req.is_verified
        if university.university_profile:
            university.university_profile.is_verified = verify_req.is_verified

        db.commit()
        db.refresh(university)

        audit_service.log_event(
            db=db,
            action=AuditAction.STATUS_CHANGE,
            entity_type="university",
            entity_id=university.id,
            description=f"Changed university '{university.name}' verification status to {verify_req.is_verified}",
            actor_user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return university


university_service = UniversityService()
