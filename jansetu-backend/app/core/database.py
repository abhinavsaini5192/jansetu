from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings
from app.core.logging_config import logger


def create_db_engine():
    """
    Creates and configures the SQLAlchemy 2.0 Engine based on settings.
    Configures connection pooling for PostgreSQL while preserving SQLite compatibility for tests.
    """
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")

    if is_sqlite:
        return create_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            connect_args={"check_same_thread": False},
        )
    else:
        # Production-grade PostgreSQL pooling
        return create_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
        )


try:
    engine = create_db_engine()
except Exception as err:
    logger.warning(
        f"Initial database engine creation warning with URL [{settings.masked_database_url}]: {err}. "
        "Will continue and handle dynamically on requests."
    )
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Shared Declarative Base class for all SQLAlchemy 2.0 models.
    Imported by Alembic (target_metadata = Base.metadata) and all entity models.
    """
    pass


def get_db() -> Generator:
    """
    FastAPI dependency yielding a request-scoped SQLAlchemy session.
    Automatically closes session in finally block to avoid any session leaks.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Database session error encountered: {exc}")
        raise
    finally:
        db.close()


def check_database_connection() -> dict:
    """
    Executes a lightweight connectivity probe (SELECT 1) against the database.
    Catches connection failures gracefully and returns a structured status dictionary
    without exposing passwords or sensitive connection strings.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "message": "Database operational",
            "dialect": engine.dialect.name,
        }
    except (OperationalError, SQLAlchemyError, Exception) as err:
        error_line = str(err).split("\n")[0]
        # Ensure passwords or full raw URLs are never leaked in error status
        sanitized_error = error_line.replace(settings.DATABASE_URL, settings.masked_database_url)
        logger.warning(f"Database connectivity check failed: {sanitized_error}")
        return {
            "status": "disconnected",
            "message": "Database is unreachable or offline",
            "dialect": getattr(engine, "dialect", None) and engine.dialect.name or "unknown",
            "error_detail": sanitized_error,
        }
