import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.enums import RiskLikelihood, RiskSeverity, RiskStatus


def calculate_risk_score(severity: RiskSeverity, likelihood: RiskLikelihood) -> int:
    """
    Computes a deterministic, transparent risk score (1 to 12).
    Severity weights: LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4
    Likelihood weights: LOW=1, MEDIUM=2, HIGH=3
    Score = severity_weight * likelihood_weight
    """
    sev_map = {
        RiskSeverity.LOW: 1,
        RiskSeverity.MEDIUM: 2,
        RiskSeverity.HIGH: 3,
        RiskSeverity.CRITICAL: 4,
    }
    lik_map = {
        RiskLikelihood.LOW: 1,
        RiskLikelihood.MEDIUM: 2,
        RiskLikelihood.HIGH: 3,
    }
    s_val = sev_map.get(severity, 2)
    l_val = lik_map.get(likelihood, 2)
    return s_val * l_val


class ProjectRisk(Base):
    """
    Project Risk Tracking Entity.
    Maintains identified execution, technical, seasonal, and resource risks along with mitigation plans.
    """
    __tablename__ = "project_risks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    severity: Mapped[RiskSeverity] = mapped_column(
        SQLEnum(
            RiskSeverity,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=RiskSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    likelihood: Mapped[RiskLikelihood] = mapped_column(
        SQLEnum(
            RiskLikelihood,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=RiskLikelihood.MEDIUM,
        nullable=False,
        index=True,
    )
    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )
    mitigation_plan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    owner_user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[RiskStatus] = mapped_column(
        SQLEnum(
            RiskStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=RiskStatus.OPEN,
        nullable=False,
        index=True,
    )
    identified_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="risks",
    )
    owner_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[owner_user_id],
    )
    identified_by_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[identified_by_user_id],
    )

    def __repr__(self) -> str:
        return f"<ProjectRisk id={self.id} project_id={self.project_id} score={self.risk_score} status={self.status}>"
