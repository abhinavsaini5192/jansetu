from typing import Generator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import user_repository

# OAuth2 scheme extracting Bearer token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=True,
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the Bearer JWT token and retrieves the current user record from database.
    Validates token signature, expiration, and ensures user existence.
    """
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Could not validate credentials: token subject missing")

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException(message="User account associated with this token no longer exists")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures that the authenticated user account is in an active state.
    """
    if not current_user.is_active:
        raise ForbiddenException(message="User account is inactive. Please contact support.")
    return current_user


# Alias for clarity
require_authenticated_user = get_current_active_user


def require_platform_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensures that the authenticated user possesses global PLATFORM_ADMIN privileges.
    """
    from app.utils.enums import UserRole

    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise ForbiddenException(message="Platform administrator privileges required.")
    return current_user


def require_organization_member(
    organization_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Validates that the current user is an active member (or platform admin) of the target organization.
    Raises 404 if organization does not exist.
    Raises 403 if user is not an active member.
    """
    from app.services.organization_service import organization_service

    # Ensure organization exists
    organization_service.get_organization(db, organization_id)
    return organization_service.check_organization_member_access(db, organization_id, current_user)


def require_organization_admin(
    organization_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Validates that the current user possesses OWNER or ADMIN privileges in the target organization
    (or is a global platform admin).
    Raises 404 if organization does not exist.
    Raises 403 if user lacks administrative authority.
    """
    from app.services.organization_service import organization_service

    # Ensure organization exists
    organization_service.get_organization(db, organization_id)
    return organization_service.check_organization_admin_access(db, organization_id, current_user)


oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)


def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
):
    """
    Attempts to retrieve the authenticated user from the Bearer token,
    returning None gracefully if unauthenticated or token invalid.
    """
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return user_repository.get_by_id(db, user_id)
    except Exception:
        return None


__all__ = [
    "get_db",
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "get_current_user_optional",
    "require_authenticated_user",
    "require_platform_admin",
    "require_organization_member",
    "require_organization_admin",
]

