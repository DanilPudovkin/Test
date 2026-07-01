"""set created_at default

Revision ID: 202606260002
Revises: 202606260001
Create Date: 2026-06-26
"""

import sqlalchemy as sa

from alembic import op

revision = "202606260002"
down_revision = "202606260001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "created_at",
        server_default=sa.func.now(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
