"""create tasks

Revision ID: 202606260001
Revises:
Create Date: 2026-06-26
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "202606260001"
down_revision = None
branch_labels = None
depends_on = None

task_priority = postgresql.ENUM(
    "LOW",
    "MEDIUM",
    "HIGH",
    name="taskpriority",
    create_type=False,
)
task_status = postgresql.ENUM(
    "NEW",
    "PENDING",
    "IN_PROGRESS",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    name="taskstatus",
    create_type=False,
)


def upgrade() -> None:
    postgresql.ENUM("LOW", "MEDIUM", "HIGH", name="taskpriority").create(
        op.get_bind(),
        checkfirst=True,
    )
    postgresql.ENUM(
        "NEW",
        "PENDING",
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        name="taskstatus",
    ).create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_created_at", "tasks", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_tasks_created_at", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_table("tasks")
    task_status.drop(op.get_bind(), checkfirst=True)
    task_priority.drop(op.get_bind(), checkfirst=True)
