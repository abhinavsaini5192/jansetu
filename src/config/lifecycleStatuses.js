/**
 * System Lifecycle Status Definitions
 * Standardized status mappings across the platform.
 */

export const LIFECYCLE_STAGES = [
  { key: "SUBMITTED", label: "Citizen Submitted", number: 1, color: "blue", path: "/citizen-portal" },
  { key: "AI_ANALYZED", label: "AI Analyzed", number: 2, color: "indigo", path: "/ai-intelligence" },
  { key: "GOVERNMENT_VALIDATED", label: "Govt Validated", number: 3, color: "amber", path: "/government-dashboard" },
  { key: "HEI_MATCHED", label: "University Matched", number: 4, color: "teal", path: "/university-matching" },
  { key: "HEI_ACCEPTED", label: "University Accepted", number: 5, color: "cyan", path: "/university-workspace" },
  { key: "TEAM_FORMED", label: "Team Formed", number: 6, color: "sky", path: "/university-workspace" },
  { key: "INDUSTRY_ATTACHED", label: "Industry Attached", number: 7, color: "purple", path: "/industry-collaboration" },
  { key: "PROTOTYPE_BUILT", label: "Prototype Built", number: 8, color: "violet", path: "/project-lifecycle" },
  { key: "PILOT_DEPLOYED", label: "Pilot Deployed", number: 9, color: "rose", path: "/project-lifecycle" },
  { key: "IMPACT_VERIFIED", label: "Impact Verified", number: 10, color: "emerald", path: "/impact-dashboard" }
];

export const STATUS_CONFIG = {
  SUBMITTED: {
    label: "Submitted",
    badgeVariant: "primary",
    color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  },
  AI_ANALYZED: {
    label: "AI Analyzed",
    badgeVariant: "teal",
    color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
  },
  GOVERNMENT_VALIDATED: {
    label: "Government Validated",
    badgeVariant: "warning",
    color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  },
  HEI_MATCHED: {
    label: "HEI Matched",
    badgeVariant: "teal",
    color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  },
  HEI_ACCEPTED: {
    label: "HEI Accepted",
    badgeVariant: "success",
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  },
  TEAM_FORMED: {
    label: "Team Formed",
    badgeVariant: "primary",
    color: "text-sky-400 bg-sky-500/10 border-sky-500/20",
  },
  INDUSTRY_ATTACHED: {
    label: "Industry Attached",
    badgeVariant: "purple",
    color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  },
  PROTOTYPE_BUILT: {
    label: "Prototype Built",
    badgeVariant: "purple",
    color: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  },
  PILOT_DEPLOYED: {
    label: "Pilot Deployed",
    badgeVariant: "warning",
    color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  },
  IMPACT_VERIFIED: {
    label: "Impact Verified",
    badgeVariant: "success",
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  },
  REJECTED: {
    label: "Rejected / Closed",
    badgeVariant: "danger",
    color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  }
};

export const getStatusDetails = (statusKey) => {
  return STATUS_CONFIG[statusKey] || {
    label: statusKey ? statusKey.replace(/_/g, ' ') : "Unknown",
    badgeVariant: "default",
    color: "text-slate-400 bg-navy-800 border-navy-700",
  };
};
