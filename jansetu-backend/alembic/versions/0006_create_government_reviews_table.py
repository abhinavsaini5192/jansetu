"""create government reviews table

Revision ID: 0006_government_reviews
Revises: 0005_attachments
Create Date: 2026-09-18 01:30:00.000000

Purpose:
Creates the 'government_reviews' table to store official validation decisions,
rejection rationales, clarification requests, and duplicate references by authorized officials.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006_government_reviews"
down_revision: Union[str, None] = "0005_attachments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "government_reviews",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("reviewer_user_id", sa.String(length=36), nullable=False),
        sa.Column("previous_status", sa.String(length=50), nullable=False),
        sa.Column("new_status", sa.String(length=50), nullable=False),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("duplicate_of_challenge_id", sa.String(length=36), nullable=True),
        sa.Column("clarification_request", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["duplicate_of_challenge_id"], ["challenges.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_government_reviews_id"), "government_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_government_reviews_challenge_id"), "government_reviews", ["challenge_id"], unique=False)
    op.create_index(op.f("ix_government_reviews_reviewer_user_id"), "government_reviews", ["reviewer_user_id"], unique=False)
    op.create_index(op.f("ix_government_reviews_duplicate_of_challenge_id"), "government_reviews", ["duplicate_of_challenge_id"], unique=False)
    op.create_index(op.f("ix_government_reviews_created_at"), "government_reviews", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_government_reviews_created_at"), table_name="government_reviews")
    op.drop_index(op.f("ix_government_reviews_duplicate_of_challenge_id"), table_name="government_reviews")
    op.drop_index(op.f("ix_government_reviews_reviewer_user_id"), table_name="government_reviews")
    op.drop_index(op.f("ix_government_reviews_challenge_id"), table_name="government_reviews")
    op.drop_index(op.f("ix_government_reviews_id"), table_name="government_reviews")
    op.drop_table("government_reviews")
