import re
from typing import List, Optional, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings managed by Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "JanSetu Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database Configuration
    DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/jansetu"

    # Optional individual DB parameters (if DATABASE_URL is not explicitly specified)
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # Connection pool configuration
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # JWT Authentication settings
    JWT_SECRET_KEY: str = "change_this_to_a_secure_random_secret_in_production_jansetu_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Allowed CORS Origins
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # File Uploads
    UPLOAD_DIR: str = "uploads/challenges"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [
        "jpg",
        "jpeg",
        "png",
        "webp",
        "pdf",
        "doc",
        "docx",
    ]

    # AI Configuration (Phase 3.1)
    AI_ENABLED: bool = False
    AI_PROVIDER: str = "none"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: Optional[str] = None
    AI_TIMEOUT_SECONDS: int = 20

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v]
        return ["*"]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        v = v.strip()
        allowed_prefixes = (
            "postgresql://",
            "postgresql+psycopg2://",
            "postgresql+asyncpg://",
            "sqlite://",
            "sqlite+pysqlite://",
        )
        if not any(v.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(
                f"Invalid database scheme in DATABASE_URL. Must start with one of: {allowed_prefixes}"
            )
        return v

    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        # If user supplied individual DB_* parameters but left DATABASE_URL default or unset
        if self.DB_HOST and self.DB_NAME and self.DB_USER:
            port_str = f":{self.DB_PORT}" if self.DB_PORT else ":5432"
            password_str = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.DB_USER}{password_str}@{self.DB_HOST}{port_str}/{self.DB_NAME}"
            )

        # Production hardening enforcement
        if self.is_production:
            self.DEBUG = False
            if "change_this_to_a_secure_random_secret" in self.JWT_SECRET_KEY:
                raise ValueError(
                    "Insecure default JWT_SECRET_KEY detected in production mode. "
                    "Set a cryptographically random JWT_SECRET_KEY in production environment."
                )
        return self

    @property
    def masked_database_url(self) -> str:
        """Returns DATABASE_URL with user credentials safely masked for logs and outputs."""
        if not self.DATABASE_URL:
            return ""
        # Mask password in URL format: scheme://user:password@host...
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", self.DATABASE_URL)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() in ("production", "prod")


settings = Settings()
