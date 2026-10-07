"""
Repository handling database persistence for Organization and OrganizationMembership entities.
"""
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.utils.enums import OrganizationMembershipRole, OrganizationType


class OrganizationRepository:
    """Repository handling database operations for Organizations and Memberships."""

    def get_by_id(self, db: Session, organization_id: str) -> Optional[Organization]:
        """Fetch an organization by its primary key ID."""
        statement = select(Organization).where(Organization.id == organization_id)
        return db.scalar(statement)

    def get_by_name(self, db: Session, name: str) -> Optional[Organization]:
        """Fetch an organization by unique name (case-insensitive)."""
        statement = select(Organization).where(func.lower(Organization.name) == name.strip().lower())
        return db.scalar(statement)

    def list_organizations(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        organization_type: Optional[OrganizationType] = None,
        district: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Organization], int]:
        """
        List organizations with filtering, search, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = select(Organization)

        if organization_type is not None:
            query = query.where(Organization.organization_type == organization_type)

        if district is not None:
            query = query.where(func.lower(Organization.district) == district.strip().lower())

        if is_active is not None:
            query = query.where(Organization.is_active == is_active)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Organization.name).like(term),
                    func.lower(Organization.legal_name).like(term),
                    func.lower(Organization.description).like(term),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.scalar(count_stmt) or 0

        # Fetch paginated items ordered by created_at desc
        stmt = query.order_by(Organization.created_at.desc()).offset(skip).limit(limit)
        items = list(db.scalars(stmt).all())

        return items, total

    def create(self, db: Session, organization: Organization) -> Organization:
        """Persist a new organization."""
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    def update(self, db: Session, organization: Organization) -> Organization:
        """Update and commit an existing organization."""
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    # Membership Methods

    def get_membership(
        self, db: Session, organization_id: str, user_id: str
    ) -> Optional[OrganizationMembership]:
        """Fetch a specific membership association by org_id and user_id."""
        statement = (
            select(OrganizationMembership)
            .options(joinedload(OrganizationMembership.user))
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user_id,
            )
        )
        return db.scalar(statement)

    def get_membership_by_id(
        self, db: Session, membership_id: str
    ) -> Optional[OrganizationMembership]:
        """Fetch a membership record by primary key ID."""
        statement = (
            select(OrganizationMembership)
            .options(joinedload(OrganizationMembership.user))
            .where(OrganizationMembership.id == membership_id)
        )
        return db.scalar(statement)

    def list_members(
        self,
        db: Session,
        organization_id: str,
        is_active: Optional[bool] = None,
    ) -> List[OrganizationMembership]:
        """List all memberships for an organization with User loaded."""
        query = (
            select(OrganizationMembership)
            .options(joinedload(OrganizationMembership.user))
            .where(OrganizationMembership.organization_id == organization_id)
        )
        if is_active is not None:
            query = query.where(OrganizationMembership.is_active == is_active)

        query = query.order_by(OrganizationMembership.joined_at.asc())
        return list(db.scalars(query).all())

    def add_membership(
        self, db: Session, membership: OrganizationMembership
    ) -> OrganizationMembership:
        """Add a new member to an organization."""
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    def update_membership(
        self, db: Session, membership: OrganizationMembership
    ) -> OrganizationMembership:
        """Update an existing membership record."""
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    def delete_membership(
        self, db: Session, membership: OrganizationMembership
    ) -> None:
        """Delete an existing membership record."""
        db.delete(membership)
        db.commit()

    def count_active_owners(self, db: Session, organization_id: str) -> int:
        """Count active owners for an organization."""
        statement = (
            select(func.count(OrganizationMembership.id))
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.membership_role == OrganizationMembershipRole.OWNER,
                OrganizationMembership.is_active == True,
            )
        )
        return db.scalar(statement) or 0


organization_repository = OrganizationRepository()
