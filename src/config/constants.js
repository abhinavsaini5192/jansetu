/**
 * Centralized Static System Constants & Categories
 * These are static UI configuration tokens, NOT business records.
 */

// Official 24 Administrative Districts of Jharkhand
export const JHARKHAND_DISTRICTS = [
  "Bokaro",
  "Chatra",
  "Deoghar",
  "Dhanbad",
  "Dumka",
  "East Singhbhum",
  "Garhwa",
  "Giridih",
  "Godda",
  "Gumla",
  "Hazaribagh",
  "Jamtara",
  "Khunti",
  "Koderma",
  "Latehar",
  "Lohardaga",
  "Pakur",
  "Palamu",
  "Ramgarh",
  "Ranchi",
  "Sahibganj",
  "Seraikela Kharsawan",
  "Simdega",
  "West Singhbhum",
];

// Standard Societal Domains
export const DOMAINS = [
  { id: "agriculture", label: "Agriculture & Food Security", labelHi: "कृषि और खाद्य सुरक्षा", icon: "Sprout" },
  { id: "water_sanitation", label: "Water & Rural Sanitation", labelHi: "जल और ग्रामीण स्वच्छता", icon: "Droplets" },
  { id: "healthcare", label: "Rural Healthcare & Nutrition", labelHi: "ग्रामीण स्वास्थ्य और पोषण", icon: "HeartPulse" },
  { id: "clean_energy", label: "Clean Energy & Electrification", labelHi: "स्वच्छ ऊर्जा और विद्युतीकरण", icon: "Zap" },
  { id: "smart_education", label: "Smart Education & Connectivity", labelHi: "स्मार्ट शिक्षा और कनेक्टिविटी", icon: "GraduationCap" },
  { id: "infrastructure", label: "Civic Infrastructure & Mobility", labelHi: "नागरिक अवसंरचना और गतिशीलता", icon: "Building2" },
  { id: "waste_management", label: "Waste Management & Environment", labelHi: "अपशिष्ट प्रबंधन और पर्यावरण", icon: "Recycle" },
  { id: "livelihood", label: "Tribal & Rural Livelihoods", labelHi: "आदिवासी और ग्रामीण आजीविका", icon: "Users" },
];

// Urgency Windows
export const URGENCY_LEVELS = [
  { id: "CRITICAL", label: "Critical (Within 14 Days)", color: "rose" },
  { id: "HIGH", label: "High (Within 30 Days)", color: "amber" },
  { id: "MEDIUM", label: "Medium (Within 60 Days)", color: "blue" },
  { id: "LOW", label: "Low (Long-Term Structural)", color: "slate" },
];

// System User Roles
export const USER_ROLES = [
  { id: "CITIZEN", label: "Citizen / Community Rep", icon: "👨‍🌾" },
  { id: "GOVERNMENT", label: "Government Official", icon: "🏛️" },
  { id: "UNIVERSITY", label: "University Faculty / Student", icon: "🎓" },
  { id: "INDUSTRY", label: "Industry / CSR Partner", icon: "🏢" },
  { id: "ADMIN", label: "System Administrator", icon: "⚙️" },
];

// Support Types for Industry Collaborators
export const INDUSTRY_SUPPORT_TYPES = [
  { id: "FUNDING", label: "Grant / Seed Funding" },
  { id: "HARDWARE", label: "Hardware & Prototype Equipment" },
  { id: "MENTORSHIP", label: "Technical Mentorship & Advisory" },
  { id: "FIELD_TESTING", label: "Field Testing & Logistics" },
  { id: "CLOUD_CREDITS", label: "Cloud & Compute Credits" },
  { id: "SCALE_DEPLOYMENT", label: "Commercial Scale Deployment" },
];
