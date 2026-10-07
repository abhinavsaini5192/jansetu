"""
Centralized System Constants and Verification Helpers for JanSetu Platform.
"""
from typing import Dict, Optional, Tuple
from app.utils.enums import SocietalDomain, normalize_enum_value

# The 24 official administrative districts of Jharkhand State (Immutable)
JHARKHAND_DISTRICTS: Tuple[str, ...] = (
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
    "Seraikela-Kharsawan",
    "Simdega",
    "West Singhbhum",
)

# Lookup dictionary for fast case-insensitive district resolution
_DISTRICT_LOOKUP: Dict[str, str] = {
    district.lower(): district for district in JHARKHAND_DISTRICTS
}

# Supported UI languages
SUPPORTED_LANGUAGES: Tuple[str, ...] = ("en", "hi")

# Pagination limits
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# Attachment upload constraints
ALLOWED_ATTACHMENT_EXTENSIONS: Tuple[str, ...] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".docx",
    ".doc",
)

ALLOWED_ATTACHMENT_MIME_TYPES: Tuple[str, ...] = (
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
)

MAX_ATTACHMENT_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

# Metadata mapping societal domains to English and Hindi display labels
DOMAIN_METADATA: Dict[str, Dict[str, str]] = {
    SocietalDomain.EDUCATION.value: {
        "label_en": "Education & Skill Development",
        "label_hi": "शिक्षा एवं कौशल विकास",
    },
    SocietalDomain.HEALTHCARE.value: {
        "label_en": "Healthcare & Nutrition",
        "label_hi": "स्वास्थ्य एवं पोषण",
    },
    SocietalDomain.AGRICULTURE.value: {
        "label_en": "Agriculture & Rural Farming",
        "label_hi": "कृषि एवं ग्रामीण खेती",
    },
    SocietalDomain.WATER.value: {
        "label_en": "Water Resources & Supply",
        "label_hi": "जल संसाधन एवं आपूर्ति",
    },
    SocietalDomain.SANITATION.value: {
        "label_en": "Sanitation & Waste Management",
        "label_hi": "स्वच्छता एवं अपशिष्ट प्रबंधन",
    },
    SocietalDomain.ENVIRONMENT.value: {
        "label_en": "Environment & Forest Conservation",
        "label_hi": "पर्यावरण एवं वन संरक्षण",
    },
    SocietalDomain.EMPLOYMENT.value: {
        "label_en": "Employment & Livelihood",
        "label_hi": "रोजगार एवं आजीविका",
    },
    SocietalDomain.LIVELIHOOD.value: {
        "label_en": "Micro-Enterprise & Self-Help",
        "label_hi": "सूक्ष्म उद्यम एवं स्वयं सहायता",
    },
    SocietalDomain.INFRASTRUCTURE.value: {
        "label_en": "Rural & Urban Infrastructure",
        "label_hi": "ग्रामीण एवं शहरी अवसंरचना",
    },
    SocietalDomain.TRANSPORTATION.value: {
        "label_en": "Transportation & Connectivity",
        "label_hi": "परिवहन एवं संपर्क",
    },
    SocietalDomain.PUBLIC_SAFETY.value: {
        "label_en": "Public Safety & Law Enforcement",
        "label_hi": "जन सुरक्षा एवं कानून व्यवस्था",
    },
    SocietalDomain.WOMEN_CHILD_WELFARE.value: {
        "label_en": "Women & Child Development",
        "label_hi": "महिला एवं बाल विकास",
    },
    SocietalDomain.TRIBAL_WELFARE.value: {
        "label_en": "Tribal Welfare & Culture",
        "label_hi": "जनजातीय कल्याण एवं संस्कृति",
    },
    SocietalDomain.RURAL_DEVELOPMENT.value: {
        "label_en": "Rural Development & Panchayats",
        "label_hi": "ग्रामीण विकास एवं पंचायत",
    },
    SocietalDomain.URBAN_DEVELOPMENT.value: {
        "label_en": "Urban Civic Amenities",
        "label_hi": "शहरी नागरिक सुविधाएं",
    },
    SocietalDomain.DIGITAL_INCLUSION.value: {
        "label_en": "Digital Inclusion & e-Governance",
        "label_hi": "डिजिटल समावेशन एवं ई-गवर्नेंस",
    },
    SocietalDomain.ENERGY.value: {
        "label_en": "Clean Energy & Electrification",
        "label_hi": "स्वच्छ ऊर्जा एवं विद्युतीकरण",
    },
    SocietalDomain.GOVERNANCE.value: {
        "label_en": "Public Grievance & Governance",
        "label_hi": "लोक शिकायत एवं सुशासन",
    },
    SocietalDomain.ACCESSIBILITY.value: {
        "label_en": "Disability Accessibility",
        "label_hi": "दिव्यांगजन सुगमता",
    },
    SocietalDomain.OTHER.value: {
        "label_en": "Other Societal Issues",
        "label_hi": "अन्य सामाजिक मुद्दे",
    },
}


def is_valid_district(district: Optional[str]) -> bool:
    """
    Checks whether a given district name matches one of the 24 official Jharkhand districts.
    Validation is case-insensitive and trims surrounding whitespace.
    """
    if not district or not isinstance(district, str):
        return False
    return district.strip().lower() in _DISTRICT_LOOKUP


def get_canonical_district(district: Optional[str]) -> Optional[str]:
    """
    Resolves input string to the official spelling and capitalization of the Jharkhand district.
    Returns None if the district is invalid.
    """
    if not district or not isinstance(district, str):
        return None
    return _DISTRICT_LOOKUP.get(district.strip().lower())


def is_valid_domain(domain: Optional[str]) -> bool:
    """
    Checks whether a given string is a valid SocietalDomain.
    """
    if not domain or not isinstance(domain, str):
        return False
    return normalize_enum_value(SocietalDomain, domain) is not None


def get_canonical_domain(domain: Optional[str]) -> Optional[str]:
    """
    Resolves an input string to canonical lowercase SocietalDomain value.
    Returns None if not recognized.
    """
    member = normalize_enum_value(SocietalDomain, domain)
    return member.value if member else None
