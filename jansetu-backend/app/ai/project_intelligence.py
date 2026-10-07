"""
AI & Rule-Based Project Intelligence Service (Phase 3.9).
Analyzes execution health, tracks milestone slippage, identifies unresolved risks,
and produces actionable next steps for project stakeholders.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload

from app.ai.schemas import ProjectIntelligenceResponse
from app.core.exceptions import NotFoundException
from app.models.deliverable import Deliverable
from app.models.milestone import Milestone
from app.models.project import Project
from app.models.project_partner import ProjectPartner
from app.models.project_risk import ProjectRisk
from app.models.proposal import Proposal
from app.utils.enums import (
    DeliverableStatus,
    MilestoneStatus,
    PartnerStatus,
    ProjectStatus,
    ProposalStatus,
    RiskSeverity,
    RiskStatus,
)


class ProjectIntelligenceService:
    """
    Project intelligence engine summarizing operational project status
    and recommending actionable next steps based on real database records.
    """

    def analyze_project(
        self,
        db: Session,
        project_id: str,
    ) -> ProjectIntelligenceResponse:
        project = (
            db.query(Project)
            .options(
                joinedload(Project.milestones).joinedload(Milestone.deliverables),
                joinedload(Project.partners),
                joinedload(Project.risks),
                joinedload(Project.proposals),
            )
            .filter(Project.id == project_id)
            .first()
        )
        if not project:
            raise NotFoundException(f"Project '{project_id}' not found.")

        now = datetime.now(timezone.utc)

        # 1. Milestone Analysis
        total_milestones = len(project.milestones)
        completed_milestones = [m for m in project.milestones if m.status == MilestoneStatus.COMPLETED]
        delayed_milestones: List[Dict[str, Any]] = []
        upcoming_milestones: List[Dict[str, Any]] = []
        pending_deliverables: List[Dict[str, Any]] = []

        for m in project.milestones:
            # Overdue check
            is_overdue = False
            if m.due_date:
                due_dt = m.due_date if m.due_date.tzinfo else m.due_date.replace(tzinfo=timezone.utc)
                if due_dt < now and m.status != MilestoneStatus.COMPLETED:
                    is_overdue = True

            m_data = {
                "id": m.id,
                "title": m.title,
                "status": m.status.value if hasattr(m.status, "value") else str(m.status),
                "due_date": m.due_date.isoformat() if m.due_date else None,
                "completion_percentage": m.completion_percentage,
            }

            if is_overdue:
                delayed_milestones.append(m_data)
            elif m.status in (MilestoneStatus.IN_PROGRESS, MilestoneStatus.PENDING):
                upcoming_milestones.append(m_data)

            # Deliverables
            for d in m.deliverables:
                if d.status != DeliverableStatus.APPROVED:
                    pending_deliverables.append({
                        "id": d.id,
                        "milestone_id": m.id,
                        "milestone_title": m.title,
                        "title": d.title,
                        "status": d.status.value if hasattr(d.status, "value") else str(d.status),
                    })

        completion_pct = 0.0
        if total_milestones > 0:
            completion_pct = round(sum(m.completion_percentage for m in project.milestones) / total_milestones, 1)

        milestone_summary = (
            f"{len(completed_milestones)} of {total_milestones} milestones completed ({completion_pct}% progress). "
            f"{len(delayed_milestones)} milestones delayed."
        )

        # 2. Risk Assessment
        open_risks: List[Dict[str, Any]] = []
        high_priority_risks: List[Dict[str, Any]] = []

        for r in project.risks:
            if r.status in (RiskStatus.OPEN, RiskStatus.MITIGATING):
                risk_data = {
                    "id": r.id,
                    "title": r.title,
                    "severity": r.severity.value if hasattr(r.severity, "value") else str(r.severity),
                    "likelihood": r.likelihood.value if hasattr(r.likelihood, "value") else str(r.likelihood),
                    "score": r.risk_score,
                    "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                    "mitigation_plan": r.mitigation_plan,
                }
                open_risks.append(risk_data)
                if r.risk_score >= 6 or r.severity == RiskSeverity.CRITICAL:
                    high_priority_risks.append(risk_data)

        # 3. Proposal Status
        accepted_proposal = next((p for p in project.proposals if p.status == ProposalStatus.ACCEPTED), None)
        under_review_proposal = next((p for p in project.proposals if p.status == ProposalStatus.UNDER_REVIEW), None)
        if accepted_proposal:
            proposal_status_str = f"Accepted (v{accepted_proposal.version})"
        elif under_review_proposal:
            proposal_status_str = f"Under Review (v{under_review_proposal.version})"
        elif project.proposals:
            proposal_status_str = "Draft Proposal Pending Review"
        else:
            proposal_status_str = "No Proposal Submitted"

        # 4. Partner Status Summary
        active_partners = [p for p in project.partners if p.status == PartnerStatus.ACCEPTED]
        if active_partners:
            partner_summary = f"{len(active_partners)} active industry/CSR partner(s) collaborating."
        elif project.partners:
            partner_summary = f"{len(project.partners)} partnership invitation(s) pending."
        else:
            partner_summary = "No industry/CSR partners attached yet."

        # 5. Warnings Generation
        warnings: List[str] = []
        if delayed_milestones:
            warnings.append(f"{len(delayed_milestones)} milestone(s) have passed their scheduled delivery due dates.")
        if high_priority_risks:
            warnings.append(f"{len(high_priority_risks)} high-impact unresolved risk(s) require active mitigation.")
        if not accepted_proposal:
            warnings.append("Project workspace operates without an officially accepted technical proposal.")
        if project.status == ProjectStatus.COMPLETED and not getattr(project, "impact_records", None):
            warnings.append("Project marked complete but no verified societal impact record is attached.")

        # 6. Actionable Next Steps
        actions: List[str] = []
        if not accepted_proposal:
            actions.append("Finalize and submit technical R&D proposal for government/university review.")
        if delayed_milestones:
            actions.append(f"Accelerate delivery for overdue milestone: '{delayed_milestones[0]['title']}'.")
        if pending_deliverables:
            actions.append(f"Upload and review pending artifact for: '{pending_deliverables[0]['title']}'.")
        if high_priority_risks:
            actions.append(f"Implement mitigation measures for critical risk: '{high_priority_risks[0]['title']}'.")
        if not active_partners:
            actions.append("Identify and invite CSR/industry partners to provide financial or equipment co-sponsorship.")
        if completion_pct >= 90.0:
            actions.append("Prepare on-ground evidence and draft societal impact assessment for state certification.")

        if not actions:
            actions.append("Project execution proceeding on schedule. Maintain active weekly check-ins.")

        summary_text = (
            f"Project '{project.title}' is currently '{project.status.value.upper()}'. "
            f"{milestone_summary} {partner_summary} Proposal status: {proposal_status_str}."
        )

        return ProjectIntelligenceResponse(
            project_id=project.id,
            project_title=project.title,
            project_summary=summary_text,
            current_status=project.status.value if hasattr(project.status, "value") else str(project.status),
            completion_percentage=completion_pct,
            milestone_summary=milestone_summary,
            delayed_milestones=delayed_milestones,
            upcoming_milestones=upcoming_milestones,
            open_risks=open_risks,
            high_priority_risks=high_priority_risks,
            pending_deliverables=pending_deliverables,
            partner_status_summary=partner_summary,
            proposal_status=proposal_status_str,
            recommended_next_actions=actions,
            warnings=warnings,
            provider="deterministic-fallback",
            fallback_used=True,
        )


project_intelligence_service = ProjectIntelligenceService()
