"""
Repository handling database persistence for Challenge entities.
Provides database access methods for creating, retrieving, filtering,
listing, updating, and deleting societal challenges.
"""
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.challenge import Challenge
from app.utils.enums import (
    ChallengeStatus,
    PriorityLevel,
    SocietalDomain,
    UrgencyLevel,
)


class ChallengeRepository:
    """Repository handling database operations for societal challenges."""

    def create_challenge(self, db: Session, challenge: Challenge) -> Challenge:
        """Persist a new Challenge entity to the database."""
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        return challenge

    # Backward compatibility alias
    create = create_challenge

    def get_challenge_by_id(self, db: Session, challenge_id: str) -> Optional[Challenge]:
        """
        Fetch a single challenge by primary key UUID.
        Eager loads submitter relationships to prevent N+1 query overhead.
        """
        statement = (
            select(Challenge)
            .options(
                joinedload(Challenge.submitted_by_user),
                joinedload(Challenge.submitted_by_organization),
            )
            .where(Challenge.id == challenge_id)
        )
        return db.scalar(statement)

    # Backward compatibility alias
    get_by_id = get_challenge_by_id

    def get_challenge_by_reference_code(self, db: Session, reference_code: str) -> Optional[Challenge]:
        """Fetch a single challenge by its human-readable reference code."""
        statement = (
            select(Challenge)
            .options(
                joinedload(Challenge.submitted_by_user),
                joinedload(Challenge.submitted_by_organization),
            )
            .where(Challenge.reference_code == reference_code.strip().upper())
        )
        return db.scalar(statement)

    # Backward compatibility alias
    get_by_reference_code = get_challenge_by_reference_code

    def list_challenges(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        district: Optional[str] = None,
        domain: Optional[SocietalDomain] = None,
        status: Optional[ChallengeStatus] = None,
        priority: Optional[PriorityLevel] = None,
        urgency: Optional[UrgencyLevel] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Challenge], int]:
        """
        List challenges with optional filtering, full-text search, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = select(Challenge).options(
            joinedload(Challenge.submitted_by_user),
            joinedload(Challenge.submitted_by_organization),
        )

        if district and district.strip():
            query = query.where(func.lower(Challenge.district) == district.strip().lower())

        if domain is not None:
            query = query.where(Challenge.domain == domain)

        if status is not None:
            query = query.where(Challenge.status == status)

        if priority is not None:
            query = query.where(Challenge.priority == priority)

        if urgency is not None:
            query = query.where(Challenge.urgency == urgency)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Challenge.title).like(term),
                    func.lower(Challenge.description).like(term),
                    func.lower(Challenge.problem_statement).like(term),
                    func.lower(Challenge.reference_code).like(term),
                )
            )

        # Calculate total count efficiently before applying pagination limits
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_query) or 0

        # Safe dynamic column sorting
        sort_column_map = {
            "created_at": Challenge.created_at,
            "submitted_at": Challenge.submitted_at,
            "updated_at": Challenge.updated_at,
            "title": Challenge.title,
            "district": Challenge.district,
            "domain": Challenge.domain,
            "priority": Challenge.priority,
            "urgency": Challenge.urgency,
            "status": Challenge.status,
        }
        sort_column = sort_column_map.get(sort_by.lower(), Challenge.created_at)

        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = db.scalars(query.offset(skip).limit(limit)).unique().all()
        return list(items), total

    def list_user_challenges(
        self,
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        district: Optional[str] = None,
        domain: Optional[SocietalDomain] = None,
        status: Optional[ChallengeStatus] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Challenge], int]:
        """
        List only challenges submitted by a specific user with filtering and pagination.
        Returns a tuple of (items, total_count).
        """
        query = (
            select(Challenge)
            .options(
                joinedload(Challenge.submitted_by_user),
                joinedload(Challenge.submitted_by_organization),
            )
            .where(Challenge.submitted_by_user_id == user_id)
        )

        if district and district.strip():
            query = query.where(func.lower(Challenge.district) == district.strip().lower())

        if domain is not None:
            query = query.where(Challenge.domain == domain)

        if status is not None:
            query = query.where(Challenge.status == status)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Challenge.title).like(term),
                    func.lower(Challenge.description).like(term),
                    func.lower(Challenge.reference_code).like(term),
                )
            )

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.scalar(count_query) or 0

        sort_column_map = {
            "created_at": Challenge.created_at,
            "submitted_at": Challenge.submitted_at,
            "updated_at": Challenge.updated_at,
            "title": Challenge.title,
            "status": Challenge.status,
        }
        sort_column = sort_column_map.get(sort_by.lower(), Challenge.created_at)

        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = db.scalars(query.offset(skip).limit(limit)).unique().all()
        return list(items), total

    def update_challenge(self, db: Session, challenge: Challenge) -> Challenge:
        """Update and commit an existing Challenge entity."""
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        return challenge

    def delete_challenge(self, db: Session, challenge: Challenge) -> None:
        """Delete a Challenge entity from the database."""
        db.delete(challenge)
        db.commit()

    def count_challenges(
        self,
        db: Session,
        status: Optional[ChallengeStatus] = None,
        district: Optional[str] = None,
        domain: Optional[SocietalDomain] = None,
    ) -> int:
        """Counts total challenges matching specified criteria."""
        query = select(func.count(Challenge.id))
        if status is not None:
            query = query.where(Challenge.status == status)
        if district and district.strip():
            query = query.where(func.lower(Challenge.district) == district.strip().lower())
        if domain is not None:
            query = query.where(Challenge.domain == domain)
        return db.scalar(query) or 0


challenge_repository = ChallengeRepository()
