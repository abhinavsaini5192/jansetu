"""Data access repositories package."""
from app.repositories.user_repository import UserRepository, user_repository
from app.repositories.organization_repository import OrganizationRepository, organization_repository
from app.repositories.challenge_repository import ChallengeRepository, challenge_repository

__all__ = [
    "UserRepository",
    "user_repository",
    "OrganizationRepository",
    "organization_repository",
    "ChallengeRepository",
    "challenge_repository",
]

