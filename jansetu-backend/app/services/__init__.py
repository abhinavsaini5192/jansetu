"""Business logic services package."""
from app.services.auth_service import AuthService, auth_service
from app.services.organization_service import OrganizationService, organization_service
from app.services.challenge_service import ChallengeService, challenge_service
from app.services.attachment_service import AttachmentService, attachment_service
from app.services.audit_service import AuditService, audit_service
from app.services.notification_service import NotificationService, notification_service
from app.services.government_service import GovernmentService, government_service
from app.services.dashboard_service import DashboardService, dashboard_service
from app.services.university_service import UniversityService, university_service
from app.services.department_service import DepartmentService, department_service
from app.services.matching_service import MatchingService, matching_service
from app.services.assignment_service import AssignmentService, assignment_service
from app.services.project_service import ProjectService, project_service
from app.services.project_activity_service import ProjectActivityService, project_activity_service
from app.services.team_service import TeamService, team_service
from app.services.proposal_service import ProposalService, proposal_service
from app.services.milestone_service import MilestoneService, milestone_service
from app.services.partner_service import PartnerService, partner_service
from app.services.risk_service import RiskService, risk_service

__all__ = [
    "AuthService",
    "auth_service",
    "OrganizationService",
    "organization_service",
    "ChallengeService",
    "challenge_service",
    "AttachmentService",
    "attachment_service",
    "AuditService",
    "audit_service",
    "NotificationService",
    "notification_service",
    "GovernmentService",
    "government_service",
    "DashboardService",
    "dashboard_service",
    "UniversityService",
    "university_service",
    "DepartmentService",
    "department_service",
    "MatchingService",
    "matching_service",
    "AssignmentService",
    "assignment_service",
    "ProjectService",
    "project_service",
    "ProjectActivityService",
    "project_activity_service",
    "TeamService",
    "team_service",
    "ProposalService",
    "proposal_service",
    "MilestoneService",
    "milestone_service",
    "PartnerService",
    "partner_service",
    "RiskService",
    "risk_service",
]
