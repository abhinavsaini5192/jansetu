from sqlalchemy import Column, ForeignKey, Table
from app.core.database import Base

department_capabilities = Table(
    "department_capabilities",
    Base.metadata,
    Column(
        "department_id",
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "capability_id",
        ForeignKey("capabilities.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)
