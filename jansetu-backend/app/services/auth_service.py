from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictException, ForbiddenException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from app.schemas.user import UserResponse
from app.utils.enums import UserRole


class AuthService:
    """Service layer handling user authentication and registration workflows."""

    def register(self, db: Session, payload: UserRegisterRequest) -> UserResponse:
        """
        Registers a new user on the platform.
        Validates email uniqueness and hashes password with bcrypt.
        """
        normalized_email = payload.email.strip().lower()

        # Check for existing account
        existing_user = user_repository.get_by_email(db, normalized_email)
        if existing_user:
            raise ConflictException(
                message=f"An account with email '{normalized_email}' already exists. Please log in."
            )

        # Hash password securely
        hashed_pwd = hash_password(payload.password)

        # Prevent self-assigning platform/government admin privileges through public registration
        assigned_role = payload.role or UserRole.CITIZEN
        if assigned_role in (UserRole.PLATFORM_ADMIN, UserRole.GOVERNMENT_ADMIN, UserRole.DISTRICT_NODAL_OFFICER):
            raise ForbiddenException("Privileged administrative and nodal roles cannot be self-assigned via public registration.")

        # Create user entity
        user = User(
            full_name=payload.full_name.strip(),
            email=normalized_email,
            password_hash=hashed_pwd,
            role=assigned_role,
            is_active=True,
            is_verified=False,
        )

        persisted_user = user_repository.create(db, user)
        return UserResponse.model_validate(persisted_user)

    def login(self, db: Session, payload: UserLoginRequest) -> TokenResponse:
        """
        Authenticates a user and produces a signed JWT access token.
        Generic failure messages are used to prevent account enumeration attacks.
        """
        normalized_email = payload.email.strip().lower()

        user = user_repository.get_by_email(db, normalized_email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException(message="Invalid email or password.")

        if not user.is_active:
            raise ForbiddenException(message="Account is inactive. Please contact platform support.")

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        user_repository.update(db, user)

        # Generate JWT with claims
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
                "full_name": user.full_name,
            },
        )

        user_resp = UserResponse.model_validate(user)

        return TokenResponse(
            access_token=access_token,
            token=access_token,
            token_type="bearer",
            user=user_resp,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )


auth_service = AuthService()
