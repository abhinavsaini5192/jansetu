"""
Deterministic Fallback AI Provider.
Provides transparent, rule-based challenge analysis, classification, entity extraction,
and capability mapping when external AI services are disabled or unavailable.
"""
import re
from typing import Any, Dict, List, Optional, Set
from app.ai.base import BaseAIProvider
from app.ai.schemas import AIAnalysisResult
from app.utils.enums import SocietalDomain, UrgencyLevel


class DeterministicFallbackProvider(BaseAIProvider):
    """
    Zero-network, deterministic rule-based analysis engine.
    Always available and transparently marked as fallback-generated.
    """

    DISTRICTS = [
        "Ranchi", "Dhanbad", "Bokaro", "Hazaribagh", "East Singhbhum", "West Singhbhum",
        "Dumka", "Deoghar", "Giridih", "Palamu", "Gumla", "Khunti", "Ramgarh",
        "Jamtara", "Godda", "Sahibganj", "Pakur", "Chatra", "Koderma", "Garhwa",
        "Latehar", "Simdega", "Seraikela Kharsawan", "Lohardaga"
    ]

    DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "agriculture": ["crop", "soil", "farmer", "farming", "harvest", "pest", "irrigation", "seed", "fertilizer", "monsoon", "yield", "paddy"],
        "water": ["water", "drinking", "arsenic", "fluoride", "contamination", "handpump", "well", "pipeline", "borewell", "drought", "supply", "filter"],
        "health": ["hospital", "clinic", "health", "doctor", "medicine", "maternal", "infant", "malnutrition", "fever", "malaria", "patient", "disease"],
        "sanitation": ["toilet", "sewage", "drainage", "garbage", "waste", "septic", "hygiene", "swachh", "cleaning", "dumping"],
        "education": ["school", "teacher", "student", "classroom", "learning", "literacy", "book", "edtech", "dropout", "curriculum"],
        "environment": ["pollution", "forest", "mine", "mining", "air", "smoke", "tree", "deforestation", "soil erosion", "conservation"],
        "infrastructure": ["road", "bridge", "culvert", "transport", "connectivity", "building", "transit", "pothole", "highway"],
        "energy": ["power", "electricity", "solar", "grid", "transformer", "outage", "blackout", "renewable", "voltage"],
        "livelihood": ["employment", "handicraft", "artisan", "tribal", "wage", "cooperative", "market", "self-help", "micro-enterprise", "skilling"],
    }

    STAKEHOLDERS: List[Dict[str, str]] = [
        {"term": "farmer", "label": "Smallholder Farmers"},
        {"term": "tribal", "label": "Indigenous & Tribal Communities"},
        {"term": "student", "label": "Primary & Secondary School Students"},
        {"term": "child", "label": "Infants & Young Children"},
        {"term": "women", "label": "Rural Women & Self-Help Groups"},
        {"term": "patient", "label": "Rural Clinic Patients"},
        {"term": "panchayat", "label": "Local Gram Panchayat"},
        {"term": "villager", "label": "Local Village Residents"},
        {"term": "worker", "label": "Daily Wage Workers"},
    ]

    CAPABILITIES_MAP: Dict[str, List[Dict[str, Any]]] = {
        "agriculture": [
            {"name": "Precision Irrigation & Soil Analysis", "weight": 40},
            {"name": "Agri-Tech & Crop Health Diagnostics", "weight": 35},
            {"name": "Rural Storage & Supply Logistics", "weight": 25},
        ],
        "water": [
            {"name": "Water Quality & Heavy Metal Testing", "weight": 40},
            {"name": "Hydrology & Watershed Engineering", "weight": 35},
            {"name": "Community Filtration Systems", "weight": 25},
        ],
        "health": [
            {"name": "Community Diagnostic Surveillance", "weight": 40},
            {"name": "Telemedicine & Rural Health IT", "weight": 30},
            {"name": "Biomedical Instrumentation Support", "weight": 30},
        ],
        "education": [
            {"name": "Digital Pedagogy & EdTech Platforms", "weight": 40},
            {"name": "Vocational Skill Engineering", "weight": 35},
            {"name": "Adaptive STEM Learning Labs", "weight": 25},
        ],
        "environment": [
            {"name": "Environmental Impact Assessment", "weight": 40},
            {"name": "Contamination Monitoring & Remediation", "weight": 35},
            {"name": "Renewable Ecological Restoration", "weight": 25},
        ],
        "infrastructure": [
            {"name": "Geotechnical & Structural Engineering", "weight": 40},
            {"name": "Rural Road Materials Testing", "weight": 35},
            {"name": "GIS & Spatial Regional Planning", "weight": 25},
        ],
        "energy": [
            {"name": "Microgrid & Solar System Design", "weight": 40},
            {"name": "Energy Efficiency Auditing", "weight": 35},
            {"name": "Battery & Storage Testing", "weight": 25},
        ],
        "sanitation": [
            {"name": "Solid & Liquid Waste Engineering", "weight": 40},
            {"name": "Sanitation Infrastructure Architecture", "weight": 35},
            {"name": "Bio-methanation Systems", "weight": 25},
        ],
        "livelihood": [
            {"name": "Micro-enterprise Tech Transfer", "weight": 40},
            {"name": "Artisan Tool Modernization", "weight": 35},
            {"name": "Supply Chain & Value Chain Optimization", "weight": 25},
        ],
    }

    @property
    def provider_name(self) -> str:
        return "deterministic-fallback"

    def classify_challenge(self, text: str) -> Dict[str, Any]:
        """Matches domain keywords and urgency markers against input text."""
        lower_text = text.lower()
        domain_scores: Dict[str, int] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in lower_text)
            if count > 0:
                domain_scores[domain] = count

        detected_domain = "general"
        confidence = 65
        if domain_scores:
            detected_domain = max(domain_scores, key=domain_scores.get)
            top_score = domain_scores[detected_domain]
            confidence = min(95, 60 + (top_score * 7))

        # Urgency detection
        urgency = "medium"
        if any(w in lower_text for w in ["death", "outbreak", "fatal", "emergency", "crisis", "toxic", "severe"]):
            urgency = "critical"
        elif any(w in lower_text for w in ["urgent", "immediate", "acute", "danger", "flooding"]):
            urgency = "high"
        elif any(w in lower_text for w in ["routine", "minor", "future", "planned", "survey"]):
            urgency = "low"

        return {
            "detected_domain": detected_domain,
            "confidence": confidence,
            "urgency_level": urgency,
        }

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extracts district locations, identified stakeholders, and prominent keywords."""
        lower_text = text.lower()

        # Locations
        found_locations = [
            dist for dist in self.DISTRICTS if dist.lower() in lower_text
        ]

        # Stakeholders
        found_stakeholders = []
        for s in self.STAKEHOLDERS:
            if s["term"] in lower_text and s["label"] not in found_stakeholders:
                found_stakeholders.append(s["label"])
        if not found_stakeholders:
            found_stakeholders.append("Local Community Residents")

        # Keywords: tokens > 3 chars, clean punctuation, non-stopwords
        stopwords = {
            "this", "that", "with", "from", "have", "been", "were", "what", "when",
            "where", "which", "there", "their", "about", "would", "could", "should",
            "these", "those", "under", "after", "before", "while", "during", "local",
        }
        tokens = re.findall(r"\b[a-zA-Z]{4,}\b", lower_text)
        freq: Dict[str, int] = {}
        for t in tokens:
            if t not in stopwords:
                freq[t] = freq.get(t, 0) + 1

        top_keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)[:8]

        return {
            "location_entities": found_locations,
            "stakeholder_entities": found_stakeholders,
            "keywords": top_keywords,
        }

    def generate_summary(self, text: str, max_words: int = 60) -> str:
        """Constructs an executive summary from problem text."""
        cleaned = re.sub(r"\s+", " ", text).strip()
        words = cleaned.split()
        if len(words) <= max_words:
            return cleaned
        return " ".join(words[:max_words]) + "..."

    def analyze_challenge(self, challenge_data: Dict[str, Any]) -> AIAnalysisResult:
        """Produces a deterministic AIAnalysisResult matching both Phase 3 and Frontend schema."""
        challenge_id = str(challenge_data.get("id", ""))
        title = challenge_data.get("title", "")
        description = challenge_data.get("description", "")
        problem_stmt = challenge_data.get("problem_statement", "")
        domain_val = challenge_data.get("domain", "")
        district_val = challenge_data.get("district", "")
        urgency_val = challenge_data.get("urgency", "medium")
        priority_val = challenge_data.get("priority", "medium")

        combined_text = f"{title} {description} {problem_stmt} {domain_val} {district_val}"

        classification = self.classify_challenge(combined_text)
        entities = self.extract_entities(combined_text)

        # Fallback to existing domain if already set on challenge
        final_domain = domain_val if domain_val else classification["detected_domain"]
        final_urgency = urgency_val if urgency_val else classification["urgency_level"]

        # Ensure district is present in location entities
        if district_val and district_val not in entities["location_entities"]:
            entities["location_entities"].insert(0, district_val)

        # Build priority score & rationale
        priority_score_map = {"low": 45, "medium": 70, "high": 85, "critical": 95}
        base_score = priority_score_map.get(str(priority_val).lower(), 70)
        if classification["urgency_level"] in ("high", "critical"):
            base_score = min(98, base_score + 10)

        priority_rationale = (
            f"Determined via deterministic assessment based on priority '{priority_val}' "
            f"and urgency marker '{final_urgency}' for domain '{final_domain}'."
        )

        # Required capabilities
        domain_key = final_domain.lower() if isinstance(final_domain, str) else "general"
        req_caps = self.CAPABILITIES_MAP.get(domain_key, [
            {"name": "Interdisciplinary Field Engineering", "weight": 50},
            {"name": "Community Impact Assessment", "weight": 50},
        ])

        # Extracted entities in format expected by 3_AiIntelligence.jsx
        extracted_entities_ui = []
        for loc in entities["location_entities"]:
            extracted_entities_ui.append({"category": "District / Location", "value": loc})
        for st in entities["stakeholder_entities"]:
            extracted_entities_ui.append({"category": "Impacted Stakeholder", "value": st})
        for kw in entities["keywords"][:4]:
            extracted_entities_ui.append({"category": "Domain Term", "value": kw.title()})

        concise_summary = self.generate_summary(problem_stmt or description or title, max_words=50)

        explanation = (
            f"Deterministic fallback analysis executed. Identified core domain as '{final_domain}' "
            f"with {len(entities['keywords'])} technical keywords and {len(entities['stakeholder_entities'])} "
            f"affected stakeholder groups in {district_val or 'Jharkhand'}."
        )

        return AIAnalysisResult(
            challenge_id=challenge_id,
            detected_domain=final_domain,
            detected_subdomain=challenge_data.get("subdomain"),
            keywords=entities["keywords"],
            location_entities=entities["location_entities"],
            stakeholder_entities=entities["stakeholder_entities"],
            urgency_level=str(final_urgency),
            affected_population_summary=str(challenge_data.get("affected_population", "")) or None,
            concise_problem_summary=concise_summary,
            suggested_tags=[kw.lower() for kw in entities["keywords"][:5]],
            explanation=explanation,
            provider=self.provider_name,
            fallback_used=True,
            # Frontend UI Compatibility
            status="COMPLETED",
            domain=final_domain.upper(),
            subDomain=challenge_data.get("subdomain") or f"{final_domain.title()} Innovation",
            domainConfidence=classification["confidence"],
            priorityScore=base_score,
            priorityLevel=str(priority_val).title(),
            priorityRationale=priority_rationale,
            extractedEntities=extracted_entities_ui,
            requiredCapabilities=req_caps,
            semanticDuplicates=[],  # Populated dynamically by service
            clusterSummary="Unique regional challenge profile registered.",
        )
