from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str = "jansetu-backend"
    version: str = "1.0.0"


class DatabaseStatus(BaseModel):
    """Database status details."""
    status: str
    message: str
    dialect: Optional[str] = None


class AIStatus(BaseModel):
    """AI availability details without secrets."""
    provider: str
    is_available: bool
    fallback_enabled: bool = True


class SystemStatusData(BaseModel):
    """System operational details."""
    application: str
    environment: str
    api_version: str
    database: DatabaseStatus
    ai: Optional[AIStatus] = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard success API response envelope."""
    success: bool = True
    data: T
    message: str = "Operation completed successfully"


class PaginationMetadata(BaseModel):
    """Pagination details."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1)
    total: int = Field(0, ge=0)
    total_pages: int = Field(0, ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated API response envelope."""
    success: bool = True
    data: List[T] = []
    items: List[T] = []
    pagination: PaginationMetadata
