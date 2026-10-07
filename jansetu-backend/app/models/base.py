"""
Declarative Base Re-export for SQLAlchemy 2.0 ORM models.
Ensures a single unified Base instance is shared across the entire application.
"""
from app.core.database import Base

__all__ = ["Base"]
