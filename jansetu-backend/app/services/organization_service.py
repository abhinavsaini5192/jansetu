"""
Business Logic Service for Organization and Membership Management.
Enforces institutional role policies, creation constraints, and member operations.
"""
from math import ceil
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.repositories.organization_repository import (
    OrganizationRepository,
    organization_repository,
)
from app.repositories.user_repository import UserRepository, user_repository
from app.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationMembershipCreateRequest,
    OrganizationMembershipUpdateRequest,
    OrganizationUpdateRequest,
)
from app.utils.enums import (
    OrganizationMembershipRole,
    OrganizationType,
    UserRole,
)


class OrganizationService:
    """Service handling business domain logic for organizations and memberships."""

    def __init__(
        self,
        org_repo: OrganizationRepository = organization_repository,
        user_repo: UserRepository = user_repository,
    ):
        self.org_repo = org_repo
        self.user_repo = user_repo

    def validate_creation_permissions(self, user: User, org_type: OrganizationType) -> None:
        """
        Enforce institution creation policy:
        - Platform admins may create any organization.
        - Government officers can create government organizations.
        - University admins can create university or research lab organizations.
        - Industry partners can create industry or startup organizations.
        - Community organizations can create NGO or community organizations.
        - Citizens, students, faculty, and researchers cannot create privileged
          (Government or University) organizations without platform approval.
        """
        if user.role == UserRole.PLATFORM_ADMIN:
            return

        privileged_types = {OrganizationType.GOVERNMENT, OrganizationType.UNIVERSITY}

        if org_type in privileged_types:
            if org_type == OrganizationType.GOVERNMENT:
                allowed_roles = {UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER}
                if user.role not in allowed_roles:
                    raise ForbiddenException(
                        message="Citizens and unauthorized users cannot create Government organizations without administrative authorization."
                    )
            elif org_type == OrganizationType.UNIVERSITY:
                allowed_roles = {UserRole.UNIVERSITY_ADMIN}
                if user.role not in allowed_roles:
                    raise ForbiddenException(
                        message="Citizens and unauthorized users cannot create University organizations without administrative authorization."
                    )

    def create_organization(
        self,
        db: Session,
        org_in: OrganizationCreateRequest,
        creator: User,
    ) -> Organization:
        """
        Creates a new organization after validating permissions and uniqueness.
        Automatically enrolls the creator as the initial Organization OWNER.
        """
        # Validate permissions
        self.validate_creation_permissions(creator, org_in.organization_type)

        # Check duplicate name (case-insensitive)
        existing = self.org_repo.get_by_name(db, org_in.name)
        if existing:
            raise ConflictException(
                message=f"An organization with the name '{org_in.name}' already exists."
            )

        # Create Organization
        organization = Organization(
            name=org_in.name,
            legal_name=org_in.legal_name,
            organization_type=org_in.organization_type,
            description=org_in.description,
            email=org_in.email,
            phone=org_in.phone,
            website=org_in.website,
            address=org_in.address,
            district=org_in.district,
            state=org_in.state,
            is_active=True,
            is_verified=False,
        )
        created_org = self.org_repo.create(db, organization)

        # Create initial OWNER membership for creator
        owner_membership = OrganizationMembership(
            user_id=creator.id,
            organization_id=created_org.id,
            membership_role=OrganizationMembershipRole.OWNER,
            is_active=True,
        )
        self.org_repo.add_membership(db, owner_membership)

        return created_org

    def get_organization(self, db: Session, organization_id: str) -> Organization:
        """Fetch an organization by ID or raise NotFoundException."""
        org = self.org_repo.get_by_id(db, organization_id)
        if not org:
            raise NotFoundException(message=f"Organization '{organization_id}' not found.")
        return org

    def list_organizations(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        organization_type: Optional[OrganizationType] = None,
        district: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Organization], int, int]:
        """
        List organizations with filtering and pagination.
        Returns (items, total, total_pages).
        """
        skip = (page - 1) * page_size
        items, total = self.org_repo.list_organizations(
            db=db,
            skip=skip,
            limit=page_size,
            organization_type=organization_type,
            district=district,
            is_active=is_active,
            search=search,
        )
        total_pages = ceil(total / page_size) if total > 0 else 0
        return items, total, total_pages

    def update_organization(
        self,
        db: Session,
        organization_id: str,
        update_in: OrganizationUpdateRequest,
        current_user: User,
    ) -> Organization:
        """
        Update organization details.
        Permitted only for Platform Admin or an active Owner/Admin of this organization.
        """
        org = self.get_organization(db, organization_id)

        # Authorization check
        self.check_organization_admin_access(db, organization_id, current_user)

        # If name is changed, check duplicate
        if update_in.name and update_in.name.lower() != org.name.lower():
            existing = self.org_repo.get_by_name(db, update_in.name)
            if existing and existing.id != org.id:
                raise ConflictException(
                    message=f"An organization with the name '{update_in.name}' already exists."
                )

        update_data = update_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)

        return self.org_repo.update(db, org)

    # Membership Management

    def check_organization_member_access(
        self,
        db: Session,
        organization_id: str,
        user: User,
    ) -> OrganizationMembership:
        """
        Verify that a user is an active member of the organization,
        or is a global platform administrator.
        """
        if user.role == UserRole.PLATFORM_ADMIN:
            # Platform admins have global access; return synthetic or existing membership
            membership = self.org_repo.get_membership(db, organization_id, user.id)
            if membership:
                return membership
            return OrganizationMembership(
                user_id=user.id,
                organization_id=organization_id,
                membership_role=OrganizationMembershipRole.ADMIN,
                is_active=True,
            )

        membership = self.org_repo.get_membership(db, organization_id, user.id)
        if not membership or not membership.is_active:
            raise ForbiddenException(
                message="You are not an active member of this organization."
            )
        return membership

    def check_organization_admin_access(
        self,
        db: Session,
        organization_id: str,
        user: User,
    ) -> OrganizationMembership:
        """
        Verify that a user is an active OWNER or ADMIN of the organization,
        or is a global platform administrator.
        """
        if user.role == UserRole.PLATFORM_ADMIN:
            membership = self.org_repo.get_membership(db, organization_id, user.id)
            if membership:
                return membership
            return OrganizationMembership(
                user_id=user.id,
                organization_id=organization_id,
                membership_role=OrganizationMembershipRole.OWNER,
                is_active=True,
            )

        membership = self.org_repo.get_membership(db, organization_id, user.id)
        if not membership or not membership.is_active:
            raise ForbiddenException(
                message="You are not an authorized administrator of this organization."
            )

        if membership.membership_role not in (
            OrganizationMembershipRole.OWNER,
            OrganizationMembershipRole.ADMIN,
        ):
            raise ForbiddenException(
                message="Administrative privileges required within this organization."
            )

        return membership

    def list_members(
        self,
        db: Session,
        organization_id: str,
        is_active: Optional[bool] = None,
    ) -> List[OrganizationMembership]:
        """List members of an organization."""
        self.get_organization(db, organization_id)
        return self.org_repo.list_members(db, organization_id, is_active=is_active)

    def add_member(
        self,
        db: Session,
        organization_id: str,
        member_in: OrganizationMembershipCreateRequest,
        current_user: User,
    ) -> OrganizationMembership:
        """
        Add a user to an organization with a designated membership role.
        Requires Org Owner/Admin or Platform Admin.
        """
        self.get_organization(db, organization_id)
        self.check_organization_admin_access(db, organization_id, current_user)

        # Verify target user exists
        target_user = self.user_repo.get_by_id(db, member_in.user_id)
        if not target_user:
            raise NotFoundException(message=f"User with ID '{member_in.user_id}' not found.")

        # Check existing membership
        existing = self.org_repo.get_membership(db, organization_id, member_in.user_id)
        if existing:
            if existing.is_active:
                raise ConflictException(
                    message="User is already an active member of this organization."
                )
            # Reactivate previously inactive membership
            existing.is_active = True
            existing.membership_role = member_in.membership_role
            return self.org_repo.update_membership(db, existing)

        membership = OrganizationMembership(
            user_id=member_in.user_id,
            organization_id=organization_id,
            membership_role=member_in.membership_role,
            is_active=True,
        )
        created_membership = self.org_repo.add_membership(db, membership)
        # Load user for response
        created_membership.user = target_user
        return created_membership

    def update_member(
        self,
        db: Session,
        organization_id: str,
        user_id: str,
        update_in: OrganizationMembershipUpdateRequest,
        current_user: User,
    ) -> OrganizationMembership:
        """
        Update a member's role or active status.
        Protects the sole owner from being demoted or deactivated.
        """
        self.get_organization(db, organization_id)
        current_membership = self.check_organization_admin_access(db, organization_id, current_user)

        target_membership = self.org_repo.get_membership(db, organization_id, user_id)
        if not target_membership:
            raise NotFoundException(message="Membership record not found.")

        # Organization Admins (non-owners) cannot modify an OWNER's role or status
        if (
            current_user.role != UserRole.PLATFORM_ADMIN
            and current_membership.membership_role != OrganizationMembershipRole.OWNER
            and target_membership.membership_role == OrganizationMembershipRole.OWNER
        ):
            raise ForbiddenException(message="Only organization owners can modify another owner.")

        # Protect the sole active owner from demotion or deactivation
        is_demoting_or_deactivating_owner = (
            target_membership.membership_role == OrganizationMembershipRole.OWNER
            and (
                (update_in.membership_role is not None and update_in.membership_role != OrganizationMembershipRole.OWNER)
                or (update_in.is_active is False)
            )
        )
        if is_demoting_or_deactivating_owner:
            owner_count = self.org_repo.count_active_owners(db, organization_id)
            if owner_count <= 1:
                raise BadRequestException(
                    message="Cannot demote or deactivate the sole owner of an organization. Assign another owner first."
                )

        if update_in.membership_role is not None:
            target_membership.membership_role = update_in.membership_role

        if update_in.is_active is not None:
            target_membership.is_active = update_in.is_active

        return self.org_repo.update_membership(db, target_membership)

    def remove_member(
        self,
        db: Session,
        organization_id: str,
        user_id: str,
        current_user: User,
    ) -> None:
        """
        Remove/delete a member from an organization.
        Permitted for Platform Admins, Org Owners, Org Admins, or the user themselves (leaving).
        Cannot remove the sole owner.
        """
        self.get_organization(db, organization_id)

        is_self_leaving = current_user.id == user_id
        if not is_self_leaving:
            self.check_organization_admin_access(db, organization_id, current_user)

        target_membership = self.org_repo.get_membership(db, organization_id, user_id)
        if not target_membership:
            raise NotFoundException(message="Membership record not found.")

        # Protect the sole active owner from removal
        if target_membership.membership_role == OrganizationMembershipRole.OWNER:
            owner_count = self.org_repo.count_active_owners(db, organization_id)
            if owner_count <= 1:
                raise BadRequestException(
                    message="Cannot remove the sole owner of an organization. Transfer ownership or assign another owner first."
                )

        self.org_repo.delete_membership(db, target_membership)


organization_service = OrganizationService()
