from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Registers a citizen or community partner with secure password hashing.",
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Creates a new user account with default CITIZEN role unless specified."""
    return auth_service.register(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Authentication",
    description="Validates credentials and issues a signed Bearer JWT token.",
)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticates credentials and returns access token and user profile."""
    return auth_service.login(db, payload)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current User Profile",
    description="Fetches authenticated profile for the caller using the Bearer token.",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Returns the authenticated user details from database."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Stateless logout endpoint allowing clients to clear session tokens.",
)
def logout():
    """Confirms logout to frontend client."""
    return {"success": True, "message": "Logged out successfully"}
