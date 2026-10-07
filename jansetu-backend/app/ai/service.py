"""
AI Intelligence Orchestrator Service.
Manages provider routing, fallback execution, and challenge analysis enrichment.
"""
import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.ai.base import BaseAIProvider
from app.ai.duplicate import duplicate_service
from app.ai.providers.external import ExternalAIProvider
from app.ai.providers.fallback import DeterministicFallbackProvider
from app.ai.schemas import AIAnalysisResult
from app.ai.similarity import similarity_service
from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.models.challenge import Challenge
from app.models.user import User
from app.services.audit_service import audit_service
from app.utils.enums import AuditAction

logger = logging.getLogger("jansetu.ai")


class AIService:
    """
    Main AI intelligence service.
    Orchestrates LLM inference with automated local deterministic fallback.
    """

    def __init__(self):
        self.fallback_provider = DeterministicFallbackProvider()
        self.external_provider = ExternalAIProvider()

    def get_active_provider(self) -> BaseAIProvider:
        """Returns configured external provider if enabled, otherwise fallback provider."""
        if settings.AI_ENABLED and self.external_provider.is_configured():
            return self.external_provider
        return self.fallback_provider

    def analyze_challenge_by_id(
        self,
        db: Session,
        challenge_id: str,
        current_user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AIAnalysisResult:
        """
        Executes AI or fallback analysis on an existing challenge in the database.
        Enriches output with live semantic duplicate clustering from the DB.
        """
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        challenge_data = {
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "problem_statement": challenge.problem_statement,
            "domain": challenge.domain.value if hasattr(challenge.domain, "value") else str(challenge.domain),
            "subdomain": challenge.subdomain,
            "district": challenge.district,
            "urgency": challenge.urgency.value if hasattr(challenge.urgency, "value") else str(challenge.urgency),
            "priority": challenge.priority.value if hasattr(challenge.priority, "value") else str(challenge.priority),
            "affected_population": challenge.affected_population,
        }

        # 1. Execute analysis (Provider with Fallback guarantee)
        provider = self.get_active_provider()
        try:
            result = provider.analyze_challenge(challenge_data)
        except Exception as exc:
            logger.warning("Provider '%s' failed: %s. Reverting to fallback.", provider.provider_name, exc)
            result = self.fallback_provider.analyze_challenge(challenge_data)

        # 2. Enrich with live database semantic duplicate detection
        try:
            dup_report = duplicate_service.check_duplicates(
                db=db,
                challenge_id=challenge.id,
                limit=4,
                minimum_score=0.25,
            )
            result.semanticDuplicates = [
                {
                    "id": dup.challenge_id,
                    "title": dup.title,
                    "similarity": dup.similarity_percentage,
                    "district": dup.district,
                }
                for dup in dup_report.possible_duplicates
            ]
            if dup_report.cluster_summary:
                result.clusterSummary = dup_report.cluster_summary
        except Exception as sim_exc:
            logger.debug("Semantic duplicate enrichment skipped: %s", sim_exc)

        # 3. Log audit event
        if current_user:
            audit_service.log_event(
                db=db,
                action=AuditAction.READ,
                entity_type="challenge_ai_analysis",
                entity_id=challenge.id,
                description=f"Generated AI problem intelligence ({result.provider}) for challenge '{challenge.reference_code}'",
                actor_user_id=current_user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return result


ai_service = AIService()
