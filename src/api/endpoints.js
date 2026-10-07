/**
 * Centralized API Endpoints
 */

export const ENDPOINTS = {
  // Auth
  AUTH: {
    ME: "/auth/me",
    LOGIN: "/auth/login",
    LOGOUT: "/auth/logout",
    REGISTER: "/auth/register",
  },

  // Dashboard & Platform Metrics
  DASHBOARD: {
    STATS: "/dashboard/stats",
    DOMAINS: "/dashboard/domains",
    DISTRICTS: "/dashboard/districts",
    RECENT_ACTIVITY: "/dashboard/activity",
  },

  // Challenges
  CHALLENGES: {
    LIST: "/challenges",
    DETAIL: (id) => `/challenges/${id}`,
    CREATE: "/challenges",
    UPDATE: (id) => `/challenges/${id}`,
    DELETE: (id) => `/challenges/${id}`,
    AI_ANALYSIS: (id) => `/challenges/${id}/ai-analysis`,
    TRIGGER_AI: (id) => `/challenges/${id}/ai-analysis/trigger`,
    MATCHES: (id) => `/challenges/${id}/matches`,
    ASSIGN_HEI: (id) => `/challenges/${id}/assign-hei`,
  },

  // Government Desk
  GOVERNMENT: {
    QUEUE: "/government/validation-queue",
    VALIDATE: (id) => `/government/challenges/${id}/validate`,
    REJECT: (id) => `/government/challenges/${id}/reject`,
    ASSIGN_DEPARTMENT: (id) => `/government/challenges/${id}/assign-department`,
    DEPARTMENTS: "/government/departments",
  },

  // Universities
  UNIVERSITIES: {
    LIST: "/universities",
    DETAIL: (id) => `/universities/${id}`,
  },

  // Industry & CSR
  INDUSTRY: {
    PARTNERS: "/industry/partners",
    DETAIL: (id) => `/industry/partners/${id}`,
    ATTACH: (projectId) => `/projects/${projectId}/partnerships`,
  },

  // Projects
  PROJECTS: {
    LIST: "/projects",
    DETAIL: (id) => `/projects/${id}`,
    BY_CHALLENGE: (challengeId) => `/challenges/${challengeId}/project`,
    CREATE: "/projects",
    UPDATE: (id) => `/projects/${id}`,
    MILESTONES: (id) => `/projects/${id}/milestones`,
    UPDATE_MILESTONE: (projectId, milestoneId) => `/projects/${projectId}/milestones/${milestoneId}`,
    TEAM: (id) => `/projects/${id}/team`,
  },

  // Impact & Verification
  IMPACT: {
    BY_CHALLENGE: (challengeId) => `/challenges/${challengeId}/impact`,
    SUBMIT_EVIDENCE: (challengeId) => `/challenges/${challengeId}/impact/evidence`,
    VERIFY: (impactId) => `/impact/${impactId}/verify`,
  },

  // Notifications
  NOTIFICATIONS: {
    LIST: "/notifications",
    MARK_READ: (id) => `/notifications/${id}/read`,
    MARK_ALL_READ: "/notifications/read-all",
  },
};
