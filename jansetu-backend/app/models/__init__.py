"""
SQLAlchemy ORM Models Package.
Registers all models with Base.metadata for application and Alembic migrations.
"""
from app.models.base import Base
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.challenge import Challenge
from app.models.attachment import Attachment
from app.models.government_review import GovernmentReview
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.university_profile import UniversityProfile
from app.models.department_capability import department_capabilities
from app.models.capability import Capability
from app.models.department import Department
from app.models.challenge_assignment import ChallengeAssignment
from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.project_team_member import ProjectTeamMember
from app.models.proposal import Proposal
from app.models.milestone import Milestone
from app.models.deliverable import Deliverable
from app.models.project_partner import ProjectPartner
from app.models.partner_support import PartnerSupport
from app.models.project_risk import ProjectRisk
from app.models.project_activity import ProjectActivity
from app.models.impact_record import ImpactRecord
from app.models.evidence_record import EvidenceRecord

__all__ = [
    "Base",
    "User",
    "Organization",
    "OrganizationMembership",
    "Challenge",
    "Attachment",
    "GovernmentReview",
    "Notification",
    "AuditLog",
    "UniversityProfile",
    "department_capabilities",
    "Capability",
    "Department",
    "ChallengeAssignment",
    "Project",
    "ProjectTeam",
    "ProjectTeamMember",
    "Proposal",
    "Milestone",
    "Deliverable",
    "ProjectPartner",
    "PartnerSupport",
    "ProjectRisk",
    "ProjectActivity",
    "ImpactRecord",
    "EvidenceRecord",
]
