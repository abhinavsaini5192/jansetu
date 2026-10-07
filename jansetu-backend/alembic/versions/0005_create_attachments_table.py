"""create attachments table

Revision ID: 0005_attachments
Revises: 0004_challenges
Create Date: 2026-09-18 01:20:00.000000

Purpose:
Creates the 'attachments' table for challenge supporting files (images, PDFs, documents)
with secure file metadata, submitter foreign key references, and cascade deletion.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_attachments"
down_revision: Union[str, None] = "0004_challenges"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("challenge_id", sa.String(length=36), nullable=False),
        sa.Column("uploaded_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_extension", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename", name="uq_attachments_stored_filename"),
    )

    op.create_index(op.f("ix_attachments_id"), "attachments", ["id"], unique=False)
    op.create_index(op.f("ix_attachments_challenge_id"), "attachments", ["challenge_id"], unique=False)
    op.create_index(op.f("ix_attachments_uploaded_by_user_id"), "attachments", ["uploaded_by_user_id"], unique=False)
    op.create_index(op.f("ix_attachments_created_at"), "attachments", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_attachments_created_at"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_uploaded_by_user_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_challenge_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_id"), table_name="attachments")
    op.drop_table("attachments")
