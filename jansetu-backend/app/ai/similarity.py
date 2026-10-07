"""
Lightweight Semantic Similarity Engine.
Implements pure-Python TF-IDF vectorization, cosine similarity,
and domain/district proximity scoring without requiring external vector databases or paid APIs.
"""
import math
import re
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from app.ai.schemas import SimilarChallengeItem, SimilarChallengesResponse
from app.core.exceptions import NotFoundException
from app.models.challenge import Challenge
from app.utils.enums import ChallengeStatus


class SimilarityService:
    """
    Deterministic TF-IDF & Cosine Similarity Service.
    Compares challenges semantically using localized NLP text representation.
    """

    STOPWORDS: Set[str] = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
        "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
        "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
        "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
        "they've", "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
        "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
        "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves", "problem", "issue", "village", "jharkhand", "area",
    }

    def normalize_text(self, text: Optional[str]) -> List[str]:
        """Tokenizes, cleans, and removes stopwords from problem text."""
        if not text:
            return []
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = [t.strip() for t in clean.split() if len(t.strip()) > 2]
        return [t for t in tokens if t not in self.STOPWORDS]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Calculates normalized term frequency for a document."""
        if not tokens:
            return {}
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        total = float(len(tokens))
        return {t: count / total for t, count in counts.items()}

    def _compute_idf(self, corpus_tokens: List[List[str]]) -> Dict[str, float]:
        """Calculates inverse document frequency across the challenge corpus."""
        n_docs = len(corpus_tokens)
        if n_docs == 0:
            return {}
        df: Dict[str, int] = {}
        for doc in corpus_tokens:
            unique_terms = set(doc)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        idf: Dict[str, float] = {}
        for t, count in df.items():
            idf[t] = math.log((1.0 + n_docs) / (1.0 + count)) + 1.0
        return idf

    def _cosine_similarity(
        self,
        vec1: Dict[str, float],
        vec2: Dict[str, float],
    ) -> float:
        """Calculates cosine similarity between two sparse TF-IDF vectors."""
        if not vec1 or not vec2:
            return 0.0
        common_keys = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def extract_challenge_content(self, challenge: Challenge) -> str:
        """Assembles rich problem representation for vectorization."""
        parts = [
            challenge.title,
            challenge.description or "",
            challenge.problem_statement or "",
            challenge.expected_outcome or "",
            challenge.domain.value if hasattr(challenge.domain, "value") else str(challenge.domain),
            challenge.district or "",
        ]
        return " ".join(p for p in parts if p)

    def find_similar_challenges(
        self,
        db: Session,
        challenge_id: str,
        limit: int = 10,
        minimum_score: float = 0.20,
        same_district_only: bool = False,
    ) -> SimilarChallengesResponse:
        """
        Finds semantically similar challenges from the database using TF-IDF cosine comparison.
        Never returns the challenge itself and excludes soft-deleted records.
        """
        target = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not target:
            raise NotFoundException(f"Challenge '{challenge_id}' not found.")

        # Query potential candidate challenges
        query = (
            db.query(Challenge)
            .filter(
                Challenge.id != challenge_id,
                Challenge.status != ChallengeStatus.REJECTED,
            )
        )
        if same_district_only and target.district:
            query = query.filter(Challenge.district.ilike(target.district.strip()))

        candidates = query.all()
        if not candidates:
            return SimilarChallengesResponse(
                challenge_id=target.id,
                total_found=0,
                similar_challenges=[],
            )

        # Build corpus tokens
        target_tokens = self.normalize_text(self.extract_challenge_content(target))
        corpus_docs = [target_tokens]
        candidate_tokens_map: Dict[str, List[str]] = {}

        for cand in candidates:
            c_tokens = self.normalize_text(self.extract_challenge_content(cand))
            candidate_tokens_map[cand.id] = c_tokens
            corpus_docs.append(c_tokens)

        # Compute IDF
        idf = self._compute_idf(corpus_docs)

        # Target TF-IDF
        target_tf = self._compute_tf(target_tokens)
        target_vec = {t: tf * idf.get(t, 1.0) for t, tf in target_tf.items()}

        results: List[SimilarChallengeItem] = []

        for cand in candidates:
            cand_tokens = candidate_tokens_map[cand.id]
            if not cand_tokens:
                continue

            cand_tf = self._compute_tf(cand_tokens)
            cand_vec = {t: tf * idf.get(t, 1.0) for t, tf in cand_tf.items()}

            text_sim = self._cosine_similarity(target_vec, cand_vec)

            # Domain and District alignment
            target_domain_str = (
                target.domain.value if hasattr(target.domain, "value") else str(target.domain)
            )
            cand_domain_str = (
                cand.domain.value if hasattr(cand.domain, "value") else str(cand.domain)
            )
            same_domain = bool(target_domain_str and target_domain_str == cand_domain_str)

            target_dist = (target.district or "").strip().lower()
            cand_dist = (cand.district or "").strip().lower()
            same_district = bool(target_dist and cand_dist and target_dist == cand_dist)

            # Combined weighted score
            # Text similarity constitutes 65%, same domain 20%, same district 15%
            bonus = 0.0
            if same_domain:
                bonus += 0.20
            if same_district:
                bonus += 0.15

            # If text similarity is very low (<0.08), suppress high bonus
            if text_sim < 0.08:
                combined_score = text_sim + (bonus * 0.25)
            else:
                combined_score = min(1.0, (text_sim * 0.65) + bonus)

            if combined_score < minimum_score:
                continue

            # Shared keywords
            shared_terms = list(set(target_tokens) & set(cand_tokens))[:6]

            # Matching reasons
            reasons: List[str] = []
            reasons.append(f"Semantic problem similarity: {int(text_sim * 100)}%")
            if same_domain:
                reasons.append(f"Shared societal domain '{target_domain_str}'")
            if same_district:
                reasons.append(f"Same geographic district '{target.district}'")
            if shared_terms:
                reasons.append(f"Shared contextual terms: {', '.join(shared_terms[:4])}")

            percentage = int(round(combined_score * 100))
            results.append(
                SimilarChallengeItem(
                    challenge_id=cand.id,
                    reference_code=cand.reference_code,
                    title=cand.title,
                    similarity_score=round(combined_score, 4),
                    similarity_percentage=percentage,
                    matching_reasons=reasons,
                    same_domain=same_domain,
                    same_district=same_district,
                    shared_keywords=shared_terms,
                    district=cand.district,
                    domain=cand_domain_str,
                )
            )

        # Sort descending by score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        results = results[:limit]

        return SimilarChallengesResponse(
            challenge_id=target.id,
            total_found=len(results),
            similar_challenges=results,
        )


similarity_service = SimilarityService()
