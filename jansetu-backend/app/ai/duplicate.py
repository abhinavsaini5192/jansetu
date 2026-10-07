"""
Advisory Duplicate Detection and Challenge Clustering Service.
Evaluates potential duplication against deterministic similarity thresholds.
Strictly non-autonomous: Government nodal officers retain sole authority for official status changes.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.ai.schemas import DuplicateCheckResponse, SimilarChallengeItem
from app.ai.similarity import similarity_service
from app.core.exceptions import NotFoundException
from app.models.challenge import Challenge


class DuplicateService:
    """
    Advisory duplicate detection service.
    Generates transparent confidence levels and recommended actions without mutating challenge status.
    """

    # Deterministic Confidence Thresholds
    THRESHOLD_HIGH = 0.75
    THRESHOLD_MEDIUM = 0.50

    def check_duplicates(
        self,
        db: Session,
        challenge_id: str,
        limit: int = 5,
        minimum_score: float = 0.35,
    ) -> DuplicateCheckResponse:
        """
        Calculates advisory duplicate likelihood for a target challenge.
        Never mutates challenge status or marks challenges as duplicate automatically.
        """
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        # Run semantic similarity lookup
        sim_response = similarity_service.find_similar_challenges(
            db=db,
            challenge_id=challenge_id,
            limit=limit,
            minimum_score=minimum_score,
            same_district_only=False,
        )

        candidates = sim_response.similar_challenges
        if not candidates:
            return DuplicateCheckResponse(
                challenge_id=challenge.id,
                possible_duplicates=[],
                highest_similarity_score=0.0,
                highest_similarity_percentage=0,
                confidence_level="LOW",
                matching_reasons=["No semantically overlapping challenges detected in the regional database."],
                recommended_action="Treat as unique regional challenge. Proceed with standard validation workflow.",
                cluster_summary="Unique regional civic ticket.",
            )

        top_match = candidates[0]
        highest_score = top_match.similarity_score
        highest_pct = top_match.similarity_percentage

        # Determine confidence level & advisory action
        if highest_score >= self.THRESHOLD_HIGH:
            confidence = "HIGH"
            action = (
                f"Flag for government review as potential duplicate of '{top_match.reference_code or top_match.challenge_id}'. "
                "Recommend government officer inspect for ticket consolidation or multi-ward linking."
            )
        elif highest_score >= self.THRESHOLD_MEDIUM:
            confidence = "MEDIUM"
            action = (
                "Review for potential regional synergy or overlapping civic report in neighboring wards. "
                "Consider collaborative institutional solver pairing."
            )
        else:
            confidence = "LOW"
            action = "Treat as distinct regional challenge. Similarity does not indicate direct duplication."

        # Compile cluster summary
        districts = {c.district for c in candidates if c.district}
        if challenge.district:
            districts.add(challenge.district)
        district_text = ", ".join(sorted(districts)) if districts else "Jharkhand"

        domain_str = challenge.domain.value if hasattr(challenge.domain, "value") else str(challenge.domain)
        cluster_summary = (
            f"Detected cluster of {len(candidates) + 1} related challenges in '{domain_str}' "
            f"across {district_text}. Highest match: {highest_pct}%."
        )

        return DuplicateCheckResponse(
            challenge_id=challenge.id,
            possible_duplicates=candidates,
            highest_similarity_score=highest_score,
            highest_similarity_percentage=highest_pct,
            confidence_level=confidence,
            matching_reasons=top_match.matching_reasons,
            recommended_action=action,
            cluster_summary=cluster_summary,
        )


duplicate_service = DuplicateService()
