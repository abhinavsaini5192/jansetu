/**
 * Role & Access Control Utilities for JanSetu Platform
 * Enforces unified identity authentication with automatic role detection.
 */

export const OFFICIAL_ROLES = [
  "GOVERNMENT",
  "GOVERNMENT_ADMIN",
  "DISTRICT_NODAL_OFFICER",
  "UNIVERSITY",
  "UNIVERSITY_ADMIN",
  "FACULTY",
  "RESEARCHER",
  "INDUSTRY",
  "INDUSTRY_PARTNER",
  "CSR_PARTNER",
  "ADMIN",
  "PLATFORM_ADMIN",
];

export const PUBLIC_ROLES = [
  "CITIZEN",
  "COMMUNITY_ORGANIZATION",
  "GUEST",
];

/**
 * Checks if a role identifier belongs to verified officials.
 * @param {string} role 
 * @returns {boolean}
 */
export const isOfficialRole = (role) => {
  if (!role) return false;
  const normalized = String(role).toUpperCase().trim();
  return OFFICIAL_ROLES.includes(normalized);
};

/**
 * Checks if a role identifier belongs to the public citizen domain.
 * @param {string} role 
 * @returns {boolean}
 */
export const isPublicRole = (role) => {
  if (!role) return true;
  const normalized = String(role).toUpperCase().trim();
  return PUBLIC_ROLES.includes(normalized);
};

/**
 * Evaluates whether a user or active session role has official clearance.
 * @param {object|null} user 
 * @param {string} [activeRole] 
 * @returns {boolean}
 */
export const isOfficialUser = (user, activeRole) => {
  if (!user && !activeRole) return false;
  if (user?.is_official === true) return true;
  if (user?.role && isOfficialRole(user.role)) return true;
  if (activeRole && isOfficialRole(activeRole)) return true;
  return false;
};

/**
 * Unified Preset Demo Accounts for fast evaluator and hackathon testing.
 * Includes both Public Citizen and Official Institutional roles.
 */
export const DEMO_PRESETS = [
  {
    id: "citizen_user",
    role: "CITIZEN",
    title: "Community Citizen Submitter",
    department: "Ranchi Gram Panchayat (Public Citizen)",
    email: "citizen@jansetu.gov.in",
    password: "CitizenPassword123!",
    icon: "👨‍🌾",
    badge: "Public Citizen",
    isOfficial: false,
    defaultRoute: "/problems",
  },
  {
    id: "govt_admin",
    role: "GOVERNMENT_ADMIN",
    title: "Er. Rajesh Verma (State Nodal Officer)",
    department: "Dept. of Drinking Water & Sanitation (Govt. of Jharkhand)",
    email: "nodal.officer@jharkhand.gov.in",
    password: "GovPassword123!",
    icon: "🏛️",
    badge: "Govt Admin",
    isOfficial: true,
    defaultRoute: "/government-dashboard",
  },
  {
    id: "university_faculty",
    role: "FACULTY",
    title: "Dr. Alok Kumar (Faculty Lead, BIT Mesra)",
    department: "Dept of Chemical & Environmental Engineering",
    email: "faculty.bit@mesra.ac.in",
    password: "FacultyPassword123!",
    icon: "🎓",
    badge: "University Faculty",
    isOfficial: true,
    universityId: "uni-bit-mesra",
    universityName: "Birla Institute of Technology (BIT) Mesra",
    defaultRoute: "/university-matching",
  },
  {
    id: "csr_lead",
    role: "CSR_PARTNER",
    title: "Sourav Roy (Chief CSR, Tata Steel Foundation)",
    department: "Tribal Development & Rural Tech Fund",
    email: "csr.lead@tatasteel.com",
    password: "CsrPassword123!",
    icon: "🏢",
    badge: "Industry CSR",
    isOfficial: true,
    defaultRoute: "/industry-collaboration",
  },
  {
    id: "platform_admin",
    role: "PLATFORM_ADMIN",
    title: "Chief Platform Administrator",
    department: "JanSetu Central Governance",
    email: "admin@jansetu.gov.in",
    password: "AdminPassword123!",
    icon: "⚙️",
    badge: "Platform Admin",
    isOfficial: true,
    defaultRoute: "/government-dashboard",
  },
];

export const OFFICIAL_PRESETS = DEMO_PRESETS.filter(p => p.isOfficial);
