"""
Advanced Explainable University Matching Engine (Phase 3.5).
Combines rule-based institutional capability evaluation with semantic keyword similarity.
Completely transparent and verifiable: Every match includes an exact score breakdown,
rationales, missing capabilities, and field proximity assessment.
Strictly non-autonomous: Government users make all official mandate decisions.
"""
import re
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session, joinedload

from app.ai.similarity import similarity_service
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.challenge import Challenge
from app.models.department import Department
from app.models.organization import Organization
from app.models.university_profile import UniversityProfile
from app.models.user import User
from app.schemas.matching import (
    ExplainableFactor,
    MatchingResponse,
    UniversityMatchResult,
)
from app.services.audit_service import audit_service
from app.utils.enums import (
    AuditAction,
    InstitutionCategory,
    OrganizationType,
    ValidationStatus,
)


class MatchingService:
    """
    Advanced Explainable Institutional Matching Service.
    Transparent weighted multi-factor scoring pairing validated civic challenges with accredited universities.
    """

    # Configurable Transparent Scoring Weights (Total: 100 points)
    WEIGHT_DOMAIN_MATCH: float = 30.0
    WEIGHT_CAPABILITY_MATCH: float = 30.0
    WEIGHT_KEYWORD_SIMILARITY: float = 15.0
    WEIGHT_GEOGRAPHIC_RELEVANCE: float = 15.0
    WEIGHT_URGENCY_COMPATIBILITY: float = 10.0

    # Domain to typical required baseline capabilities
    EXPECTED_DOMAIN_CAPABILITIES: Dict[str, List[str]] = {
        "water": ["water quality", "filtration", "hydrology", "testing"],
        "agriculture": ["soil analysis", "irrigation", "agri-tech", "crop"],
        "health": ["diagnostics", "telemedicine", "surveillance", "clinical"],
        "sanitation": ["waste management", "drainage", "sanitation", "treatment"],
        "education": ["pedagogy", "edtech", "digital learning", "curriculum"],
        "environment": ["impact assessment", "pollution monitoring", "remediation"],
        "infrastructure": ["geotechnical", "materials testing", "civil", "structural"],
        "energy": ["microgrid", "solar", "renewable", "storage"],
        "livelihood": ["micro-enterprise", "skilling", "supply chain", "value chain"],
    }

    def match_universities_for_challenge(
        self,
        db: Session,
        challenge_id: str,
        current_user: Optional[User] = None,
        limit: Optional[int] = None,
        minimum_score: Optional[float] = None,
        district: Optional[str] = None,
        domain: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MatchingResponse:
        """
        Executes explainable multi-factor matching for a validated challenge.
        Calculates transparent scores out of 100 based on domain, capabilities, semantic keywords,
        proximity, and category readiness.
        """
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        # Eligibility rule: only validated challenges can enter institutional matching
        if challenge.validation_status != ValidationStatus.VALIDATED:
            raise BadRequestException(
                f"Only validated challenges can be matched with institutions. Current status is '{challenge.validation_status.value}'."
            )

        # Retrieve all active and verified universities with profiles and departments
        query = (
            db.query(Organization)
            .options(
                joinedload(Organization.university_profile),
                joinedload(Organization.departments).joinedload(Department.capabilities),
            )
            .filter(
                Organization.organization_type == OrganizationType.UNIVERSITY,
                Organization.is_active == True,
                Organization.is_verified == True,
            )
        )

        if district:
            query = query.filter(Organization.district.ilike(district.strip()))

        universities = query.all()

        challenge_text = f"{challenge.title} {challenge.description or ''} {challenge.problem_statement or ''}"
        challenge_tokens = set(similarity_service.normalize_text(challenge_text))
        target_district = (challenge.district or "").strip().lower()
        target_domain = challenge.domain
        target_domain_str = target_domain.value if hasattr(target_domain, "value") else str(target_domain)

        match_results: List[UniversityMatchResult] = []

        for uni in universities:
            reasons: List[str] = []
            matched_domains: Set[str] = set()
            matched_capabilities: List[str] = []
            best_department: Optional[Department] = None
            best_dept_cap_count = 0

            # 1. Domain Alignment Scoring (Max: WEIGHT_DOMAIN_MATCH = 30 pts)
            domain_matched = False
            for dept in uni.departments:
                dept_caps_in_domain = 0
                for cap in dept.capabilities:
                    cap_domain_str = cap.domain.value if hasattr(cap.domain, "value") else str(cap.domain)
                    if cap_domain_str.lower() == target_domain_str.lower():
                        domain_matched = True
                        matched_domains.add(cap_domain_str)
                        matched_capabilities.append(cap.name)
                        dept_caps_in_domain += 1

                if dept_caps_in_domain > best_dept_cap_count:
                    best_dept_cap_count = dept_caps_in_domain
                    best_department = dept

            if domain_matched:
                domain_score = self.WEIGHT_DOMAIN_MATCH
                domain_reason = f"Accredited department directly aligns with challenge domain '{target_domain_str}'."
                reasons.append(domain_reason)
            else:
                dept_names = " ".join([d.name.lower() for d in uni.departments])
                if target_domain_str.replace("_", " ") in dept_names:
                    domain_score = self.WEIGHT_DOMAIN_MATCH * 0.60
                    domain_reason = f"University hosts departments relevant to domain '{target_domain_str}'."
                    reasons.append(domain_reason)
                else:
                    domain_score = self.WEIGHT_DOMAIN_MATCH * 0.35
                    domain_reason = "Multidisciplinary academic baseline competence."

            # 2. Capability Match Scoring (Max: WEIGHT_CAPABILITY_MATCH = 30 pts)
            registered_cap_count = len(matched_capabilities)
            if registered_cap_count >= 3:
                cap_score = self.WEIGHT_CAPABILITY_MATCH
                cap_reason = f"Strong R&D capability match: {registered_cap_count} specialized lab capabilities registered."
                reasons.append(cap_reason)
            elif registered_cap_count >= 1:
                cap_score = self.WEIGHT_CAPABILITY_MATCH * 0.75
                cap_reason = f"Relevant department capabilities active: {', '.join(matched_capabilities[:2])}."
                reasons.append(cap_reason)
            else:
                cap_score = self.WEIGHT_CAPABILITY_MATCH * 0.30
                cap_reason = "General engineering and institutional faculty support available."

            # 3. Semantic Keyword Similarity (Max: WEIGHT_KEYWORD_SIMILARITY = 15 pts)
            uni_text = f"{uni.name} "
            for dept in uni.departments:
                uni_text += f"{dept.name} {dept.description or ''} "
                for cap in dept.capabilities:
                    uni_text += f"{cap.name} {cap.keywords or ''} {cap.description or ''} "

            uni_tokens = set(similarity_service.normalize_text(uni_text))
            shared_keywords = list(challenge_tokens & uni_tokens)

            if len(shared_keywords) >= 3:
                kw_score = self.WEIGHT_KEYWORD_SIMILARITY
                kw_reason = f"Semantic match across challenge keywords: {', '.join(shared_keywords[:4])}."
                reasons.append(kw_reason)
            elif len(shared_keywords) >= 1:
                kw_score = self.WEIGHT_KEYWORD_SIMILARITY * 0.65
                kw_reason = f"Partial semantic keyword alignment: {', '.join(shared_keywords)}."
                reasons.append(kw_reason)
            else:
                kw_score = self.WEIGHT_KEYWORD_SIMILARITY * 0.25
                kw_reason = "Foundational technical terminology alignment."

            # 4. Geographic Relevance / Field Proximity (Max: WEIGHT_GEOGRAPHIC_RELEVANCE = 15 pts)
            uni_district = (uni.district or "").strip().lower()
            district_match = bool(target_district and uni_district and uni_district == target_district)
            if district_match:
                dist_score = self.WEIGHT_GEOGRAPHIC_RELEVANCE
                dist_reason = f"Located in target district '{challenge.district}', enabling rapid field deployment and ground pilot."
                reasons.append(dist_reason)
            else:
                dist_score = self.WEIGHT_GEOGRAPHIC_RELEVANCE * 0.60
                dist_reason = f"Located in {uni.district or 'Jharkhand'}, capable of state-wide regional deployment."

            # 5. Urgency & Category Readiness (Max: WEIGHT_URGENCY_COMPATIBILITY = 10 pts)
            prof = uni.university_profile
            category = prof.institution_category if prof else InstitutionCategory.UNIVERSITY

            if category in (InstitutionCategory.ENGINEERING_COLLEGE, InstitutionCategory.TECHNICAL_INSTITUTE):
                urgency_score = self.WEIGHT_URGENCY_COMPATIBILITY
                urgency_reason = "Technical & Engineering institution equipped for rapid prototype turnaround."
            elif category == InstitutionCategory.RESEARCH_INSTITUTE:
                urgency_score = self.WEIGHT_URGENCY_COMPATIBILITY
                urgency_reason = "Specialized Research Institute equipped with accredited analytical lab facilities."
            elif category == InstitutionCategory.MEDICAL_COLLEGE and target_domain_str in ("health", "healthcare", "water", "sanitation"):
                urgency_score = self.WEIGHT_URGENCY_COMPATIBILITY
                urgency_reason = "Medical College directly aligned for clinical and public health validation."
            else:
                urgency_score = self.WEIGHT_URGENCY_COMPATIBILITY * 0.80
                urgency_reason = "Comprehensive Higher Education Institution capacity."

            reasons.append(urgency_reason)

            # Total score calculation
            total_raw = domain_score + cap_score + kw_score + dist_score + urgency_score
            total_score = round(min(100.0, total_raw), 1)
            int_score = int(round(total_score))

            # Missing capabilities analysis
            expected_caps = self.EXPECTED_DOMAIN_CAPABILITIES.get(target_domain_str.lower(), ["field engineering"])
            missing = []
            registered_caps_lower = [c.lower() for c in matched_capabilities]
            for exp in expected_caps:
                if not any(exp in rc for rc in registered_caps_lower):
                    missing.append(f"Specialized {exp.title()} Module")

            # Explainable factors for Screen 05
            explainable_factors = {
                "domain_alignment": ExplainableFactor(
                    label="Domain Alignment",
                    score=int(round((domain_score / self.WEIGHT_DOMAIN_MATCH) * 100)),
                    reason=domain_reason,
                ),
                "capability_keywords": ExplainableFactor(
                    label="Capability & R&D Readiness",
                    score=int(round(((cap_score + kw_score) / (self.WEIGHT_CAPABILITY_MATCH + self.WEIGHT_KEYWORD_SIMILARITY)) * 100)),
                    reason=cap_reason,
                ),
                "district_proximity": ExplainableFactor(
                    label="Field Proximity",
                    score=int(round((dist_score / self.WEIGHT_GEOGRAPHIC_RELEVANCE) * 100)),
                    reason=dist_reason,
                ),
                "institution_readiness": ExplainableFactor(
                    label="Institutional Category Readiness",
                    score=int(round((urgency_score / self.WEIGHT_URGENCY_COMPATIBILITY) * 100)),
                    reason=urgency_reason,
                ),
            }

            score_breakdown = {
                "domain_match": round(domain_score, 1),
                "capability_match": round(cap_score, 1),
                "keyword_similarity": round(kw_score, 1),
                "geographic_relevance": round(dist_score, 1),
                "urgency_compatibility": round(urgency_score, 1),
            }

            explanation = (
                f"Overall score {total_score}% computed via explainable multi-factor formula. "
                f"Domain match: {domain_score}/{self.WEIGHT_DOMAIN_MATCH}, "
                f"Capabilities: {cap_score}/{self.WEIGHT_CAPABILITY_MATCH}, "
                f"Keywords: {kw_score}/{self.WEIGHT_KEYWORD_SIMILARITY}, "
                f"Proximity: {dist_score}/{self.WEIGHT_GEOGRAPHIC_RELEVANCE}. "
                f"{dist_reason}"
            )

            location_display = f"{uni.district or 'Jharkhand'}, Jharkhand"
            accreditation_display = (prof.accreditation_details if prof and prof.accreditation_details else "Accredited HEI")
            strengths = matched_capabilities[:4] if matched_capabilities else [d.name for d in uni.departments[:3]]
            if not strengths:
                strengths = ["Applied Engineering", "Community Innovation"]

            result = UniversityMatchResult(
                university_id=uni.id,
                university_name=uni.name,
                department_id=best_department.id if best_department else None,
                department_name=best_department.name if best_department else None,
                score=int_score,
                total_score=total_score,
                score_breakdown=score_breakdown,
                reasons=reasons,
                match_reasons=reasons,
                matched_domains=list(matched_domains),
                matched_capabilities=matched_capabilities,
                missing_capabilities=missing[:3],
                explanation=explanation,
                district_match=district_match,
                eligibility_status="ELIGIBLE",
                data_source="explainable-hybrid-matching",
                # Frontend compatibility fields
                id=uni.id,
                universityId=uni.id,
                name=uni.name,
                overallMatch=int_score,
                location=location_display,
                type=category.value.replace("_", " ").title(),
                accreditation=accreditation_display,
                strengths=strengths,
                explainableFactors=explainable_factors,
            )

            if minimum_score is not None and total_score < minimum_score:
                continue

            match_results.append(result)

        # Sort descending by score
        match_results.sort(key=lambda m: m.total_score, reverse=True)

        if limit is not None:
            match_results = match_results[:limit]

        # Record audit log
        if current_user:
            audit_service.log_event(
                db=db,
                action=AuditAction.READ,
                entity_type="challenge_match",
                entity_id=challenge_id,
                description=f"Generated {len(match_results)} explainable institutional matches for challenge '{challenge.reference_code}'",
                actor_user_id=current_user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return MatchingResponse(
            challenge_id=challenge.id,
            challenge_title=challenge.title,
            challenge_domain=target_domain_str,
            challenge_district=challenge.district or "Jharkhand",
            total_candidates=len(match_results),
            matches=match_results,
            disclaimer="Advisory recommendation only. Government users make all official mandate decisions.",
        )


matching_service = MatchingService()
