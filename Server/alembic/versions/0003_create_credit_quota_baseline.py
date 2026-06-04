"""create credit quota baseline

Revision ID: 0003_create_credit_quota_baseline
Revises: 0002_create_v1_domain_baseline
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_create_credit_quota_baseline"
down_revision = "0002_create_v1_domain_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ux_credit_ledger_idempotency_key", table_name="credit_ledger")
    op.create_index(
        "ux_credit_ledger_user_idempotency_key",
        "credit_ledger",
        ["user_id", "idempotency_key"],
        unique=True,
    )
    op.create_table(
        "credit_balance_snapshots",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("bucket", sa.String(length=32), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("ledger_version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "bucket"),
    )
    op.create_table(
        "quota_counters",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False),
        sa.Column("feature", sa.String(length=64), nullable=False),
        sa.Column("period_type", sa.String(length=32), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("used_amount", sa.Integer(), nullable=False),
        sa.Column("limit_amount", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quota_counters_user_id", "quota_counters", ["user_id"])
    op.create_index("ix_quota_counters_user_updated", "quota_counters", ["user_id", "updated_at"])
    op.create_index(
        "ux_quota_counters_user_feature_period",
        "quota_counters",
        ["user_id", "feature", "period_type", "period_start"],
        unique=True,
    )
    op.create_table(
        "plan_allowances",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False),
        sa.Column("feature", sa.String(length=64), nullable=False),
        sa.Column("period_type", sa.String(length=32), nullable=False),
        sa.Column("limit_amount", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plan_allowances_enabled", "plan_allowances", ["enabled"])
    op.create_index(
        "ux_plan_allowances_plan_feature_period_version",
        "plan_allowances",
        ["plan", "feature", "period_type", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_plan_allowances_plan_feature_period_version", table_name="plan_allowances")
    op.drop_index("ix_plan_allowances_enabled", table_name="plan_allowances")
    op.drop_table("plan_allowances")
    op.drop_index("ux_quota_counters_user_feature_period", table_name="quota_counters")
    op.drop_index("ix_quota_counters_user_updated", table_name="quota_counters")
    op.drop_index("ix_quota_counters_user_id", table_name="quota_counters")
    op.drop_table("quota_counters")
    op.drop_table("credit_balance_snapshots")
    op.drop_index("ux_credit_ledger_user_idempotency_key", table_name="credit_ledger")
    op.create_index("ux_credit_ledger_idempotency_key", "credit_ledger", ["idempotency_key"], unique=True)
