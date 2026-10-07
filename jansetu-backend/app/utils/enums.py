from enum import Enum
from typing import Any, List, Optional, Type, TypeVar

T = TypeVar("T", bound=Enum)


class UserRole(str, Enum):
    """
    Platform User Roles.
    Controls role-based access control (RBAC) across citizen, institution,
    government, and platform administration tiers.
    """
    CITIZEN = "citizen"
    COMMUNITY_ORGANIZATION = "community_organization"
    GOVERNMENT_ADMIN = "government_admin"
    DISTRICT_NODAL_OFFICER = "district_nodal_officer"
    UNIVERSITY_ADMIN = "university_admin"
    FACULTY = "faculty"
    STUDENT = "student"
    RESEARCHER = "researcher"
    INDUSTRY_PARTNER = "industry_partner"
    CSR_PARTNER = "csr_partner"
    PLATFORM_ADMIN = "platform_admin"


class OrganizationType(str, Enum):
    """
    Organization Categories.
    Classifies external institutions, academic bodies, and government departments.
    """
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    INDUSTRY = "industry"
    NGO = "ngo"
    COMMUNITY = "community"
    RESEARCH_LAB = "research_lab"
    STARTUP = "startup"


class OrganizationMembershipRole(str, Enum):
    """
    Organization-Scoped Member Roles.
    Distinguishes administrative and contributor privileges within an institution.
    """
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChallengeStatus(str, Enum):
    """
    Societal Challenge Lifecycle Status.
    Represents the operational stage of an intake challenge at the platform governance level.
    """
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    NEEDS_CLARIFICATION = "needs_clarification"
    ASSIGNED = "assigned"


class ValidationStatus(str, Enum):
    """
    Government Review & Verification Status.
    Captures the evaluation outcome reached by government nodal reviewers.
    """
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    NEEDS_CLARIFICATION = "needs_clarification"


class PriorityLevel(str, Enum):
    """
    Administrative Priority Level.
    Designates execution urgency and intervention priority assigned by nodal officers.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UrgencyLevel(str, Enum):
    """
    Citizen-Reported Urgency Level.
    Designates citizen perception of community impact at time of intake.
    Separated from PriorityLevel to allow distinct governance weighting.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """
    Platform Notification Categories.
    Specifies user alert types triggered by system state changes.
    """
    CHALLENGE_SUBMITTED = "challenge_submitted"
    CHALLENGE_VALIDATED = "challenge_validated"
    CHALLENGE_REJECTED = "challenge_rejected"
    CHALLENGE_MARKED_DUPLICATE = "challenge_marked_duplicate"
    CLARIFICATION_REQUESTED = "clarification_requested"
    DEPARTMENT_ASSIGNED = "department_assigned"
    SYSTEM = "system"
    SECURITY = "security"
    GENERAL = "general"


class AuditAction(str, Enum):
    """
    Auditable System Events.
    Standardized actions recorded in the immutable platform audit log.
    """
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    SUBMIT = "submit"
    VALIDATE = "validate"
    REJECT = "reject"
    MARK_DUPLICATE = "mark_duplicate"
    REQUEST_CLARIFICATION = "request_clarification"
    ASSIGN_DEPARTMENT = "assign_department"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    STATUS_CHANGE = "status_change"


class SocietalDomain(str, Enum):
    """
    Societal Innovation Domains.
    Categorizes problems into sectoral disciplines across Jharkhand.
    """
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    AGRICULTURE = "agriculture"
    WATER = "water"
    SANITATION = "sanitation"
    ENVIRONMENT = "environment"
    EMPLOYMENT = "employment"
    LIVELIHOOD = "livelihood"
    INFRASTRUCTURE = "infrastructure"
    TRANSPORTATION = "transportation"
    PUBLIC_SAFETY = "public_safety"
    WOMEN_CHILD_WELFARE = "women_child_welfare"
    TRIBAL_WELFARE = "tribal_welfare"
    RURAL_DEVELOPMENT = "rural_development"
    URBAN_DEVELOPMENT = "urban_development"
    DIGITAL_INCLUSION = "digital_inclusion"
    ENERGY = "energy"
    GOVERNANCE = "governance"
    ACCESSIBILITY = "accessibility"
    OTHER = "other"


class InstitutionCategory(str, Enum):
    """
    Higher Education Institution (HEI) Categories.
    Classifies academic and research bodies for specialized mandate matching.
    """
    UNIVERSITY = "university"
    ENGINEERING_COLLEGE = "engineering_college"
    MEDICAL_COLLEGE = "medical_college"
    POLYTECHNIC = "polytechnic"
    DEGREE_COLLEGE = "degree_college"
    RESEARCH_INSTITUTE = "research_institute"
    TECHNICAL_INSTITUTE = "technical_institute"
    OTHER = "other"


class AssignmentStatus(str, Enum):
    """
    Challenge Assignment / Institutional Mandate Lifecycle Status.
    """
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class ProjectStatus(str, Enum):
    """
    Project Workspace Execution Status.
    """
    CREATED = "created"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TeamRole(str, Enum):
    """
    Multidisciplinary Project Team Roles.
    """
    TEAM_LEAD = "team_lead"
    FACULTY_MENTOR = "faculty_mentor"
    STUDENT = "student"
    RESEARCHER = "researcher"
    CONTRIBUTOR = "contributor"


class ProposalStatus(str, Enum):
    """
    Solution Proposal Review and Acceptance Status.
    """
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class MilestoneStatus(str, Enum):
    """
    Project Milestone Execution Status.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliverableStatus(str, Enum):
    """
    Milestone Deliverable Evaluation Status.
    """
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class PartnerType(str, Enum):
    """
    External Collaborative Partner Classification.
    """
    INDUSTRY = "industry"
    CSR = "csr"
    STARTUP = "startup"
    NGO = "ngo"
    RESEARCH_PARTNER = "research_partner"


class PartnerStatus(str, Enum):
    """
    Partner Invitation and Collaboration Lifecycle Status.
    """
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SupportType(str, Enum):
    """
    Partner Resource Support Categories.
    """
    FUNDING = "funding"
    EQUIPMENT = "equipment"
    EXPERTISE = "expertise"
    MENTORSHIP = "mentorship"
    INFRASTRUCTURE = "infrastructure"
    INTERNSHIP = "internship"
    TRAINING = "training"
    TECHNOLOGY = "technology"
    OTHER = "other"


class SupportStatus(str, Enum):
    """
    Partner Support Commitment Status.
    """
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class RiskSeverity(str, Enum):
    """
    Project Risk Severity Levels.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLikelihood(str, Enum):
    """
    Project Risk Occurrence Likelihood.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskStatus(str, Enum):
    """
    Project Risk Mitigation Status.
    """
    OPEN = "open"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class ProjectActivityType(str, Enum):
    """
    Project Activity Audit & Timeline Types.
    """
    PROJECT_CREATED = "project_created"
    TEAM_CREATED = "team_created"
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    PROPOSAL_SUBMITTED = "proposal_submitted"
    PROPOSAL_REVIEWED = "proposal_reviewed"
    MILESTONE_CREATED = "milestone_created"
    MILESTONE_UPDATED = "milestone_updated"
    DELIVERABLE_SUBMITTED = "deliverable_submitted"
    DELIVERABLE_REVIEWED = "deliverable_reviewed"
    PARTNER_INVITED = "partner_invited"
    PARTNER_ACCEPTED = "partner_accepted"
    SUPPORT_ADDED = "support_added"
    RISK_CREATED = "risk_created"
    RISK_UPDATED = "risk_updated"
    STATUS_CHANGED = "status_changed"
    IMPACT_SUBMITTED = "impact_submitted"
    IMPACT_VERIFIED = "impact_verified"
    IMPACT_REJECTED = "impact_rejected"
    EVIDENCE_SUBMITTED = "evidence_submitted"
    EVIDENCE_VERIFIED = "evidence_verified"


class ImpactType(str, Enum):
    """
    Impact Categories for verified societal outcomes.
    """
    SOCIAL = "social"
    EDUCATIONAL = "educational"
    ECONOMIC = "economic"
    HEALTH = "health"
    ENVIRONMENTAL = "environmental"
    INFRASTRUCTURE = "infrastructure"
    DIGITAL_INCLUSION = "digital_inclusion"
    LIVELIHOOD = "livelihood"
    GOVERNANCE = "governance"
    OTHER = "other"


class ImpactStatus(str, Enum):
    """
    Impact Record Lifecycle Status.
    """
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


class EvidenceType(str, Enum):
    """
    Format and Source Categorization of Field Impact Evidence.
    """
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    REPORT = "report"
    SURVEY = "survey"
    BENEFICIARY_FEEDBACK = "beneficiary_feedback"
    OFFICIAL_RECORD = "official_record"
    OTHER = "other"


class EvidenceVerificationStatus(str, Enum):
    """
    State Evaluation Status for Submitted Field Evidence.
    """
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


def enum_values(enum_cls: Type[Enum]) -> List[str]:
    """Returns a list of all string values defined on an enum class."""
    return [member.value for member in enum_cls]


def normalize_enum_value(enum_cls: Type[T], value: Optional[Any]) -> Optional[T]:
    """
    Safely normalizes input strings (case-insensitively by name or value)
    into the corresponding enum member. Returns None if invalid or absent.
    """
    if value is None:
        return None
    if isinstance(value, enum_cls):
        return value

    val_str = str(value).strip().lower()

    # Try matching by enum value first
    for member in enum_cls:
        if member.value.lower() == val_str:
            return member

    # Try matching by enum member name
    name_str = str(value).strip().upper()
    for member in enum_cls:
        if member.name == name_str:
            return member

    return None
