"""
Base AI Provider Interface.
Defines abstract contracts for challenge analysis, classification, entity extraction, and summarization.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.ai.schemas import AIAnalysisResult


class BaseAIProvider(ABC):
    """Abstract base class for all AI intelligence providers (external and fallback)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical name of the provider."""
        pass

    @abstractmethod
    def analyze_challenge(self, challenge_data: Dict[str, Any]) -> AIAnalysisResult:
        """Analyzes a structured challenge record and returns a comprehensive AIAnalysisResult."""
        pass

    @abstractmethod
    def classify_challenge(self, text: str) -> Dict[str, Any]:
        """Classifies raw problem text into domain, subdomain, and urgency level."""
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extracts location entities, stakeholders, and technical keywords from text."""
        pass

    @abstractmethod
    def generate_summary(self, text: str, max_words: int = 60) -> str:
        """Generates an executive problem summary from detailed problem text."""
        pass
