"""create impact and evidence tables (Phases 3.6 & 3.7)

Revision ID: 0011_impact_and_evidence
Revises: 0010_project_collaboration
Create Date: 2026-09-18 12:30:00.000000

Purpose:
Creates tables for verified societal outcomes and auditable field evidence:
- impact_records
- evidence_records
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0011_impact_and_evidence"
down_revision: Union[str, None] = "0010_project_collaboration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. impact_records
    op.create_table(
        "impact_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=True),
        sa.Column("submitted_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("impact_type", sa.String(length=50), nullable=False, server_default="social"),
        sa.Column("target_population", sa.String(length=255), nullable=True),
        sa.Column("actual_beneficiaries", sa.String(length=255), nullable=True),
        sa.Column("geographic_coverage", sa.String(length=255), nullable=True),
        sa.Column("villages_covered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("baseline_value", sa.String(length=255), nullable=True),
        sa.Column("achieved_value", sa.String(length=255), nullable=True),
        sa.Column("measurement_unit", sa.String(length=100), nullable=True),
        sa.Column("outcome_summary", sa.Text(), nullable=True),
        sa.Column("economic_benefit", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("verified_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submitted_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["verified_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_impact_records_project_id", "impact_records", ["project_id"])
    op.create_index("ix_impact_records_challenge_id", "impact_records", ["challenge_id"])
    op.create_index("ix_impact_records_status", "impact_records", ["status"])

    # 2. evidence_records
    op.create_table(
        "evidence_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("impact_record_id", sa.String(length=36), nullable=False),
        sa.Column("submitted_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("attachment_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("evidence_type", sa.String(length=50), nullable=False, server_default="document"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("capture_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_reference", sa.String(length=255), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("verified_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["attachment_id"], ["attachments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["impact_record_id"], ["impact_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submitted_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["verified_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidence_records_impact_record_id", "evidence_records", ["impact_record_id"])
    op.create_index("ix_evidence_records_verification_status", "evidence_records", ["verification_status"])


def downgrade() -> None:
    op.drop_table("evidence_records")
    op.drop_table("impact_records")
