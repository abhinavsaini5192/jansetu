"""initial baseline migration

Revision ID: 0001_baseline
Revises: None
Create Date: 2026-09-17 23:50:00.000000

Purpose:
Establishes the Alembic schema version tracking baseline for JanSetu.
No business tables are created prematurely in Phase 1.2.
Subsequent subphases (Phase 1.4 - 1.16) will introduce entity tables
(organizations, users, challenges, etc.).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline placeholder: no operational tables created until entity definitions in later subphases
    pass


def downgrade() -> None:
    pass
