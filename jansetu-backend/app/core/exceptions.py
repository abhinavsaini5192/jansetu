from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging_config import logger


class JanSetuException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundException(JanSetuException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class BadRequestException(JanSetuException):
    def __init__(self, message: str = "Bad request", code: str = "BAD_REQUEST", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedException(JanSetuException):
    def __init__(self, message: str = "Authentication required", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenException(JanSetuException):
    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ConflictException(JanSetuException):
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class DatabaseUnavailableException(JanSetuException):
    def __init__(self, message: str = "Database service is temporarily unavailable", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="DATABASE_OFFLINE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class PayloadTooLargeException(JanSetuException):
    def __init__(self, message: str = "File size exceeds allowed limit", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="PAYLOAD_TOO_LARGE",
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            details=details,
        )


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Helper to construct standardized error envelopes."""
    payload = {
        "success": False,
        "message": message,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers on the FastAPI application."""

    @app.exception_handler(JanSetuException)
    async def jansetu_exception_handler(request: Request, exc: JanSetuException):
        logger.warning(f"JanSetuException: {exc.code} - {exc.message} on {request.url.path}")
        return build_error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        formatted_errors = []
        for err in exc.errors():
            formatted_errors.append({
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg"),
                "type": err.get("type"),
            })
        return build_error_response(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY),
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=formatted_errors,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "RESOURCE_NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"

        return build_error_response(
            status_code=exc.status_code,
            code=code,
            message=str(exc.detail),
            details=None,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled server error on {request.url.path}: {exc}")
        return build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred. Please try again later.",
            details=str(exc) if not app.state.settings.is_production else None,
        )
