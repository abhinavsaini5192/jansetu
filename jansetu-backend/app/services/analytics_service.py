"""
Platform Analytics and Reporting Service (Phase 3.8).
Executes real PostgreSQL / SQLite SQL aggregation queries for governance metrics.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.impact_record import ImpactRecord
from app.models.milestone import Milestone
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_partner import ProjectPartner
from app.models.project_risk import ProjectRisk
from app.models.proposal import Proposal
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    ChallengesAnalyticsResponse,
    DistrictAnalyticsItem,
    DomainAnalyticsItem,
    ImpactAnalyticsResponse,
    ProjectsAnalyticsResponse,
)
from app.utils.enums import (
    ChallengeStatus,
    ImpactStatus,
    MilestoneStatus,
    OrganizationType,
    ProjectStatus,
    ProposalStatus,
    RiskStatus,
    ValidationStatus,
)


class AnalyticsService:
    """Computes real database-backed platform metrics, summaries, and breakdowns."""

    def get_overview(self, db: Session) -> AnalyticsOverviewResponse:
        # 1. Challenges
        total_challenges = db.scalar(select(func.count(Challenge.id))) or 0
        val_challenges = db.scalar(
            select(func.count(Challenge.id)).where(Challenge.validation_status == ValidationStatus.VALIDATED)
        ) or 0

        c_status_rows = db.execute(select(Challenge.status, func.count(Challenge.id)).group_by(Challenge.status)).all()
        c_status_dict = {str(k.value if hasattr(k, "value") else k): v for k, v in c_status_rows if k is not None}

        # 2. Projects
        total_projects = db.scalar(select(func.count(Project.id))) or 0
        p_status_rows = db.execute(select(Project.status, func.count(Project.id)).group_by(Project.status)).all()
        p_status_dict = {str(k.value if hasattr(k, "value") else k): v for k, v in p_status_rows if k is not None}

        active_projects = p_status_dict.get(ProjectStatus.ACTIVE.value, 0)
        completed_projects = p_status_dict.get(ProjectStatus.COMPLETED.value, 0)

        # 3. Organizations
        total_unis = db.scalar(
            select(func.count(Organization.id)).where(
                Organization.organization_type == OrganizationType.UNIVERSITY,
                Organization.is_active == True,
            )
        ) or 0
        total_partners = db.scalar(
            select(func.count(Organization.id)).where(
                Organization.organization_type.in_([OrganizationType.INDUSTRY, OrganizationType.NGO, OrganizationType.STARTUP]),
                Organization.is_active == True,
            )
        ) or 0

        # 4. Impact
        total_impact = db.scalar(select(func.count(ImpactRecord.id))) or 0
        verified_impact = db.scalar(
            select(func.count(ImpactRecord.id)).where(ImpactRecord.status == ImpactStatus.VERIFIED)
        ) or 0
        imp_status_rows = db.execute(select(ImpactRecord.status, func.count(ImpactRecord.id)).group_by(ImpactRecord.status)).all()
        imp_status_dict = {str(k.value if hasattr(k, "value") else k): v for k, v in imp_status_rows if k is not None}

        return AnalyticsOverviewResponse(
            total_challenges=total_challenges,
            validated_challenges=val_challenges,
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_universities=total_unis,
            total_partners=total_partners,
            total_impact_records=total_impact,
            verified_impact_records=verified_impact,
            challenges_by_status=c_status_dict,
            projects_by_status=p_status_dict,
            impact_by_status=imp_status_dict,
        )

    def get_challenges_analytics(self, db: Session) -> ChallengesAnalyticsResponse:
        total = db.scalar(select(func.count(Challenge.id))) or 0
        validated = db.scalar(
            select(func.count(Challenge.id)).where(Challenge.validation_status == ValidationStatus.VALIDATED)
        ) or 0

        # Group by status
        status_rows = db.execute(select(Challenge.status, func.count(Challenge.id)).group_by(Challenge.status)).all()
        by_status = {str(k.value if hasattr(k, "value") else k): v for k, v in status_rows if k is not None}

        # Group by domain
        domain_rows = db.execute(select(Challenge.domain, func.count(Challenge.id)).group_by(Challenge.domain)).all()
        by_domain = {str(k.value if hasattr(k, "value") else k): v for k, v in domain_rows if k is not None}

        # Group by district
        district_rows = db.execute(select(Challenge.district, func.count(Challenge.id)).group_by(Challenge.district)).all()
        by_district = {str(k): v for k, v in district_rows if k is not None}

        # Group by priority
        priority_rows = db.execute(select(Challenge.priority, func.count(Challenge.id)).group_by(Challenge.priority)).all()
        by_priority = {str(k.value if hasattr(k, "value") else k): v for k, v in priority_rows if k is not None}

        # Group by urgency
        urgency_rows = db.execute(select(Challenge.urgency, func.count(Challenge.id)).group_by(Challenge.urgency)).all()
        by_urgency = {str(k.value if hasattr(k, "value") else k): v for k, v in urgency_rows if k is not None}

        return ChallengesAnalyticsResponse(
            total_challenges=total,
            validated_challenges=validated,
            by_status=by_status,
            by_domain=by_domain,
            by_district=by_district,
            by_priority=by_priority,
            by_urgency=by_urgency,
        )

    def get_projects_analytics(self, db: Session) -> ProjectsAnalyticsResponse:
        total_projects = db.scalar(select(func.count(Project.id))) or 0
        p_status_rows = db.execute(select(Project.status, func.count(Project.id)).group_by(Project.status)).all()
        by_status = {str(k.value if hasattr(k, "value") else k): v for k, v in p_status_rows if k is not None}

        total_proposals = db.scalar(select(func.count(Proposal.id))) or 0
        accepted_proposals = db.scalar(
            select(func.count(Proposal.id)).where(Proposal.status == ProposalStatus.APPROVED)
        ) or 0

        total_milestones = db.scalar(select(func.count(Milestone.id))) or 0
        completed_milestones = db.scalar(
            select(func.count(Milestone.id)).where(Milestone.status == MilestoneStatus.COMPLETED)
        ) or 0

        active_risks = db.scalar(
            select(func.count(ProjectRisk.id)).where(ProjectRisk.status.in_([RiskStatus.OPEN, RiskStatus.MITIGATING]))
        ) or 0

        total_partnerships = db.scalar(select(func.count(ProjectPartner.id))) or 0

        return ProjectsAnalyticsResponse(
            total_projects=total_projects,
            by_status=by_status,
            total_proposals=total_proposals,
            accepted_proposals=accepted_proposals,
            total_milestones=total_milestones,
            completed_milestones=completed_milestones,
            active_risks_count=active_risks,
            total_partnerships=total_partnerships,
        )

    def get_impact_analytics(self, db: Session) -> ImpactAnalyticsResponse:
        total_impact = db.scalar(select(func.count(ImpactRecord.id))) or 0
        verified_impact = db.scalar(
            select(func.count(ImpactRecord.id)).where(ImpactRecord.status == ImpactStatus.VERIFIED)
        ) or 0
        total_villages = db.scalar(select(func.sum(ImpactRecord.villages_covered))) or 0

        by_type_rows = db.execute(select(ImpactRecord.impact_type, func.count(ImpactRecord.id)).group_by(ImpactRecord.impact_type)).all()
        by_type = {str(k.value if hasattr(k, "value") else k): v for k, v in by_type_rows if k is not None}

        by_status_rows = db.execute(select(ImpactRecord.status, func.count(ImpactRecord.id)).group_by(ImpactRecord.status)).all()
        by_status = {str(k.value if hasattr(k, "value") else k): v for k, v in by_status_rows if k is not None}

        pct = round((verified_impact / total_impact * 100), 1) if total_impact > 0 else 0.0

        return ImpactAnalyticsResponse(
            total_impact_records=total_impact,
            verified_impact_records=verified_impact,
            total_villages_covered=int(total_villages),
            by_impact_type=by_type,
            by_status=by_status,
            verified_percentage=pct,
        )

    def get_districts_analytics(self, db: Session) -> List[DistrictAnalyticsItem]:
        # Count challenges per district
        stmt = (
            select(
                Challenge.district,
                func.count(Challenge.id).label("total"),
                func.count(Challenge.id).filter(Challenge.validation_status == ValidationStatus.VALIDATED).label("val"),
            )
            .group_by(Challenge.district)
            .order_by(desc("total"))
        )
        rows = db.execute(stmt).all()

        results = []
        for dist, total, val in rows:
            if not dist:
                continue
            # Active projects in this district
            p_count = db.scalar(
                select(func.count(Project.id))
                .join(Challenge, Project.challenge_id == Challenge.id)
                .where(Challenge.district == dist, Project.status == ProjectStatus.ACTIVE)
            ) or 0

            # Villages covered in this district
            v_count = db.scalar(
                select(func.sum(ImpactRecord.villages_covered))
                .join(Challenge, ImpactRecord.challenge_id == Challenge.id)
                .where(Challenge.district == dist)
            ) or 0

            results.append(
                DistrictAnalyticsItem(
                    district=dist,
                    total_challenges=total,
                    validated_challenges=val,
                    active_projects=p_count,
                    villages_covered=int(v_count),
                )
            )
        return results

    def get_domains_analytics(self, db: Session) -> List[DomainAnalyticsItem]:
        stmt = (
            select(
                Challenge.domain,
                func.count(Challenge.id).label("total"),
                func.count(Challenge.id).filter(Challenge.validation_status == ValidationStatus.VALIDATED).label("val"),
            )
            .group_by(Challenge.domain)
            .order_by(desc("total"))
        )
        rows = db.execute(stmt).all()

        results = []
        for dom, total, val in rows:
            if not dom:
                continue
            dom_str = dom.value if hasattr(dom, "value") else str(dom)

            p_count = db.scalar(
                select(func.count(Project.id))
                .join(Challenge, Project.challenge_id == Challenge.id)
                .where(Challenge.domain == dom, Project.status.in_([ProjectStatus.ACTIVE, ProjectStatus.COMPLETED]))
            ) or 0

            imp_count = db.scalar(
                select(func.count(ImpactRecord.id))
                .join(Challenge, ImpactRecord.challenge_id == Challenge.id)
                .where(Challenge.domain == dom)
            ) or 0

            results.append(
                DomainAnalyticsItem(
                    domain=dom_str,
                    total_challenges=total,
                    validated_challenges=val,
                    active_projects=p_count,
                    impact_records=imp_count,
                )
            )
        return results


analytics_service = AnalyticsService()
