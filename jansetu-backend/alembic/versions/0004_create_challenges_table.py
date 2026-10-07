"""create challenge model

Revision ID: 0004_challenges
Revises: 0003_organizations
Create Date: 2026-09-18 00:50:00.000000

Purpose:
Creates the 'challenges' table for societal issues submitted by citizens,
community organizations, and NGOs, with full location metadata, centralized
domain/priority/status classifications, and submitter foreign key references.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_challenges"
down_revision: Union[str, None] = "0003_organizations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reference_code", sa.String(length=32), nullable=False),
        sa.Column("submitted_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("submitted_by_organization_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("title_hi", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=True),
        sa.Column("proposed_context", sa.Text(), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("block", sa.String(length=100), nullable=True),
        sa.Column("village_or_ward", sa.String(length=100), nullable=True),
        sa.Column("location_description", sa.String(length=500), nullable=True),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column("subdomain", sa.String(length=100), nullable=True),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("urgency", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="submitted"),
        sa.Column("validation_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("assigned_department", sa.String(length=255), nullable=True),
        sa.Column("affected_population", sa.String(length=255), nullable=True),
        sa.Column("estimated_beneficiaries", sa.Integer(), nullable=True),
        sa.Column("existing_attempts", sa.Text(), nullable=True),
        sa.Column("expected_outcome", sa.Text(), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duplicate_of_challenge_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["submitted_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["submitted_by_organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["duplicate_of_challenge_id"], ["challenges.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_code", name="uq_challenges_reference_code"),
    )

    op.create_index(op.f("ix_challenges_id"), "challenges", ["id"], unique=False)
    op.create_index(op.f("ix_challenges_reference_code"), "challenges", ["reference_code"], unique=True)
    op.create_index(op.f("ix_challenges_status"), "challenges", ["status"], unique=False)
    op.create_index(op.f("ix_challenges_validation_status"), "challenges", ["validation_status"], unique=False)
    op.create_index(op.f("ix_challenges_district"), "challenges", ["district"], unique=False)
    op.create_index(op.f("ix_challenges_domain"), "challenges", ["domain"], unique=False)
    op.create_index(op.f("ix_challenges_priority"), "challenges", ["priority"], unique=False)
    op.create_index(op.f("ix_challenges_urgency"), "challenges", ["urgency"], unique=False)
    op.create_index(op.f("ix_challenges_submitted_by_user_id"), "challenges", ["submitted_by_user_id"], unique=False)
    op.create_index(op.f("ix_challenges_submitted_by_organization_id"), "challenges", ["submitted_by_organization_id"], unique=False)
    op.create_index(op.f("ix_challenges_created_at"), "challenges", ["created_at"], unique=False)
    op.create_index(op.f("ix_challenges_duplicate_of_challenge_id"), "challenges", ["duplicate_of_challenge_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_challenges_duplicate_of_challenge_id"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_created_at"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_submitted_by_organization_id"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_submitted_by_user_id"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_urgency"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_priority"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_domain"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_district"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_validation_status"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_status"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_reference_code"), table_name="challenges")
    op.drop_index(op.f("ix_challenges_id"), table_name="challenges")
    op.drop_table("challenges")
