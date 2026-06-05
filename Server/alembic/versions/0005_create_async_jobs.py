"""create async jobs

Revision ID: 0005_create_async_jobs
Revises: 0004_create_date_event_rule_baseline
Create Date: 2026-06-05
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_create_async_jobs"
down_revision = "0004_create_date_event_rule_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "async_jobs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("result_ref", sa.String(length=128), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_async_jobs_user_id", "async_jobs", ["user_id"])
    op.create_index("ix_async_jobs_user_created", "async_jobs", ["user_id", "created_at"])
    op.create_index(
        "ix_async_jobs_type_status_priority_created",
        "async_jobs",
        ["job_type", "status", "priority", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_async_jobs_type_status_priority_created", table_name="async_jobs")
    op.drop_index("ix_async_jobs_user_created", table_name="async_jobs")
    op.drop_index("ix_async_jobs_user_id", table_name="async_jobs")
    op.drop_table("async_jobs")
