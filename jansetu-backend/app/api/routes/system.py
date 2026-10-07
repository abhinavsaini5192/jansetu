from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.common import (
    AIStatus,
    ApiResponse,
    DatabaseStatus,
    HealthResponse,
    SystemStatusData,
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns service vitality status.",
    tags=["System"],
)
def get_health():
    """Returns basic health status for load balancers and container monitors."""
    return HealthResponse(
        status="healthy",
        service="jansetu-backend",
        version="1.0.0",
    )


@router.get(
    "/system/status",
    response_model=ApiResponse[SystemStatusData],
    summary="System Runtime Status",
    description="Detailed operational metadata including database connectivity.",
    tags=["System"],
)
def get_system_status():
    """Returns application name, active environment, API version, database, and AI status without exposing secrets."""
    db_check = check_database_connection()

    has_ai_key = bool(
        getattr(settings, "GEMINI_API_KEY", None)
        or getattr(settings, "OPENAI_API_KEY", None)
    )

    status_data = SystemStatusData(
        application=settings.APP_NAME,
        environment=settings.APP_ENV,
        api_version="v1",
        database=DatabaseStatus(
            status=db_check.get("status", "unknown"),
            message=db_check.get("message", "unknown"),
            dialect=db_check.get("dialect"),
        ),
        ai=AIStatus(
            provider=getattr(settings, "AI_PROVIDER", "fallback"),
            is_available=has_ai_key,
            fallback_enabled=True,
        ),
    )

    return ApiResponse(
        success=True,
        data=status_data,
        message="System status retrieved successfully",
    )
