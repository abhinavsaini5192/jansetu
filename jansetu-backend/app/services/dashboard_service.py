"""
Dashboard Service for JanSetu Platform.
Provides real aggregated platform metrics, district distributions,
sectoral breakdowns, and recent activity from database queries.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.challenge import Challenge
from app.models.notification import Notification
from app.models.user import User
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    DistrictCountItem,
    DomainCountItem,
    RecentActivityItem,
)
from app.utils.constants import DOMAIN_METADATA, JHARKHAND_DISTRICTS
from app.utils.enums import ChallengeStatus, SocietalDomain, ValidationStatus


class DashboardService:
    """Service computing aggregated statistics from PostgreSQL records."""

    def get_overview(self, db: Session, current_user: Optional[User] = None) -> DashboardOverviewResponse:
        """
        Calculates platform-wide challenge status counts and caller's unread notifications.
        Uses real SQL COUNT aggregation without mock data.
        """
        # Query challenge counts grouped by status
        status_stmt = select(Challenge.status, func.count(Challenge.id)).group_by(Challenge.status)
        status_results = dict(db.execute(status_stmt).all())

        total_stmt = select(func.count(Challenge.id))
        total_challenges = db.scalar(total_stmt) or 0

        # Unread notifications count
        unread_notifs = 0
        if current_user:
            notif_stmt = select(func.count(Notification.id)).where(
                Notification.recipient_user_id == current_user.id,
                Notification.is_read == False,
            )
            unread_notifs = db.scalar(notif_stmt) or 0

        submitted = status_results.get(ChallengeStatus.SUBMITTED, 0)
        under_review = status_results.get(ChallengeStatus.UNDER_REVIEW, 0)
        validated = status_results.get(ChallengeStatus.VALIDATED, 0)
        rejected = status_results.get(ChallengeStatus.REJECTED, 0)
        duplicate = status_results.get(ChallengeStatus.DUPLICATE, 0)
        needs_clarification = status_results.get(ChallengeStatus.NEEDS_CLARIFICATION, 0)
        assigned = status_results.get(ChallengeStatus.ASSIGNED, 0)

        return DashboardOverviewResponse(
            total_challenges=total_challenges,
            submitted_challenges=submitted,
            under_review_challenges=under_review,
            validated_challenges=validated,
            rejected_challenges=rejected,
            duplicate_challenges=duplicate,
            clarification_needed_challenges=needs_clarification,
            assigned_challenges=assigned,
            unread_notifications_count=unread_notifs,
        )

    def get_district_summary(self, db: Session) -> List[DistrictCountItem]:
        """Calculates challenge count and validated count per Jharkhand district."""
        stmt = (
            select(
                Challenge.district,
                func.count(Challenge.id).label("total"),
                func.count(Challenge.id).filter(Challenge.status == ChallengeStatus.VALIDATED).label("validated"),
            )
            .group_by(Challenge.district)
            .order_by(desc("total"))
        )
        rows = db.execute(stmt).all()

        items = []
        for district_name, count, validated_count in rows:
            items.append(
                DistrictCountItem(
                    district=district_name,
                    count=count,
                    validated_count=validated_count,
                )
            )

        return items

    def get_domain_summary(self, db: Session) -> List[DomainCountItem]:
        """Calculates challenge count per societal domain with localized labels."""
        stmt = (
            select(Challenge.domain, func.count(Challenge.id))
            .group_by(Challenge.domain)
            .order_by(desc(func.count(Challenge.id)))
        )
        rows = db.execute(stmt).all()

        items = []
        for domain_enum, count in rows:
            domain_val = domain_enum.value if hasattr(domain_enum, "value") else str(domain_enum)
            metadata = DOMAIN_METADATA.get(domain_val, {})
            items.append(
                DomainCountItem(
                    domain=domain_val,
                    count=count,
                    label=metadata.get("label_en", domain_val.capitalize()),
                )
            )

        return items

    def get_recent_activity(self, db: Session, limit: int = 10) -> List[RecentActivityItem]:
        """Fetches latest platform activity from the immutable audit log."""
        stmt = (
            select(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        logs = db.scalars(stmt).all()

        activity = []
        for entry in logs:
            activity.append(
                RecentActivityItem(
                    id=entry.id,
                    type=entry.action,
                    title=f"{entry.action.capitalize()} on {entry.entity_type}",
                    description=entry.description,
                    timestamp=entry.created_at,
                )
            )

        return activity


dashboard_service = DashboardService()
