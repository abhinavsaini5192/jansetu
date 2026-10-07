from fastapi import APIRouter
from app.api.routes import (
    ai,
    analytics,
    assignments,
    attachments,
    audit_logs,
    auth,
    challenges,
    dashboard,
    departments,
    government,
    impact,
    matching,
    milestones,
    notifications,
    organizations,
    partners,
    projects,
    proposals,
    risks,
    system,
    teams,
    timeline,
    universities,
)

api_router = APIRouter()

# Mount system routes (provides /system/status and /health under API prefix)
api_router.include_router(system.router, tags=["System"])

# Authentication routes (Phase 1.4)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Organizations routes (Phase 1.5)
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

# Challenges routes (Phase 1.7)
api_router.include_router(challenges.router, prefix="/challenges", tags=["Challenges"])

# Attachments routes (Phase 1.8)
api_router.include_router(attachments.router, tags=["Attachments"])

# Government Validation routes (Phase 1.9)
api_router.include_router(government.router, prefix="/government", tags=["Government"])

# Notifications routes (Phase 1.10)
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Audit Logs routes (Phase 1.10)
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])

# Dashboard routes (Phase 1.11)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# University Directory routes (Phase 2.1)
api_router.include_router(universities.router, prefix="/universities", tags=["Universities"])

# Department & Capability routes (Phase 2.2)
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])

# Matching & Challenge Assignment routes (Phases 2.3 & 2.4)
api_router.include_router(matching.router, prefix="/challenges", tags=["Matching & Assignments"])

# Assignment Decisions routes (Phase 2.4)
api_router.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])

# Project Workspace routes (Phase 2.5)
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Team Management routes (Phase 2.6)
api_router.include_router(teams.router, tags=["Teams"])

# Proposal Management routes (Phase 2.7)
api_router.include_router(proposals.router, tags=["Proposals"])

# Milestones & Deliverables routes (Phase 2.8)
api_router.include_router(milestones.router, tags=["Milestones & Deliverables"])

# Industry & CSR Collaboration routes (Phase 2.9)
api_router.include_router(partners.router, tags=["Industry & CSR Partnerships"])

# Project Risks routes (Phase 2.10)
api_router.include_router(risks.router, tags=["Project Risks"])

# Activity Timeline routes (Phase 2.10)
api_router.include_router(timeline.router, tags=["Project Timeline"])

# AI Problem Intelligence & Semantic Similarity routes (Phases 3.1 - 3.4)
api_router.include_router(ai.router, prefix="/ai", tags=["AI Problem Intelligence & Similarity"])

# Platform Analytics & Reporting routes (Phase 3.8)
api_router.include_router(analytics.router, prefix="/analytics", tags=["Platform Analytics & Reporting"])

# Impact Assessment & Evidence Verification routes (Phases 3.6 & 3.7)
api_router.include_router(impact.router, tags=["Impact & Evidence Management"])
