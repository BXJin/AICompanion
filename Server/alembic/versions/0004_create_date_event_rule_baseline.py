"""create date event rule baseline

Revision ID: 0004_create_date_event_rule_baseline
Revises: 0003_create_credit_quota_baseline
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_create_date_event_rule_baseline"
down_revision = "0003_create_credit_quota_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "date_event_templates",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("event_code", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("required_relationship_level", sa.Integer(), nullable=False),
        sa.Column("entry_cost", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("reward_policy_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_date_event_templates_public", "date_event_templates", ["enabled", "status"])
    op.create_index("ux_date_event_templates_code_version", "date_event_templates", ["event_code", "version"], unique=True)
    op.create_table(
        "date_game_sessions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("template_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result", sa.String(length=32), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("state_json", sa.JSON(), nullable=False),
        sa.Column("reward_event_id", sa.String(length=64), nullable=True),
        sa.Column("relationship_event_id", sa.String(length=64), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["date_event_templates.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_date_game_sessions_character_id", "date_game_sessions", ["character_id"])
    op.create_index("ix_date_game_sessions_template_id", "date_game_sessions", ["template_id"])
    op.create_index("ix_date_game_sessions_user_character_started", "date_game_sessions", ["user_id", "character_id", "started_at"])
    op.create_index("ix_date_game_sessions_user_id", "date_game_sessions", ["user_id"])
    op.create_index("ix_date_game_sessions_user_status_started", "date_game_sessions", ["user_id", "status", "started_at"])
    op.create_index("ux_date_game_sessions_user_idempotency_key", "date_game_sessions", ["user_id", "idempotency_key"], unique=True)
    op.create_table(
        "game_moves",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("actor", sa.String(length=32), nullable=False),
        sa.Column("move_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("rule_result_json", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["date_game_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_game_moves_session_id", "game_moves", ["session_id"])
    op.create_index("ux_game_moves_session_idempotency_key", "game_moves", ["session_id", "idempotency_key"], unique=True)
    op.create_index("ux_game_moves_session_sequence", "game_moves", ["session_id", "sequence_no"], unique=True)
    op.create_table(
        "reward_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("reward_type", sa.String(length=32), nullable=False),
        sa.Column("reward_ref", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rule_version", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reward_events_character_id", "reward_events", ["character_id"])
    op.create_index("ix_reward_events_user_character_created", "reward_events", ["user_id", "character_id", "created_at"])
    op.create_index("ix_reward_events_user_id", "reward_events", ["user_id"])
    op.create_index("ux_reward_events_source_reward", "reward_events", ["user_id", "source_type", "source_id", "reward_type"], unique=True)


def downgrade() -> None:
    op.drop_index("ux_reward_events_source_reward", table_name="reward_events")
    op.drop_index("ix_reward_events_user_id", table_name="reward_events")
    op.drop_index("ix_reward_events_user_character_created", table_name="reward_events")
    op.drop_index("ix_reward_events_character_id", table_name="reward_events")
    op.drop_table("reward_events")
    op.drop_index("ux_game_moves_session_sequence", table_name="game_moves")
    op.drop_index("ux_game_moves_session_idempotency_key", table_name="game_moves")
    op.drop_index("ix_game_moves_session_id", table_name="game_moves")
    op.drop_table("game_moves")
    op.drop_index("ux_date_game_sessions_user_idempotency_key", table_name="date_game_sessions")
    op.drop_index("ix_date_game_sessions_user_status_started", table_name="date_game_sessions")
    op.drop_index("ix_date_game_sessions_user_id", table_name="date_game_sessions")
    op.drop_index("ix_date_game_sessions_user_character_started", table_name="date_game_sessions")
    op.drop_index("ix_date_game_sessions_template_id", table_name="date_game_sessions")
    op.drop_index("ix_date_game_sessions_character_id", table_name="date_game_sessions")
    op.drop_table("date_game_sessions")
    op.drop_index("ux_date_event_templates_code_version", table_name="date_event_templates")
    op.drop_index("ix_date_event_templates_public", table_name="date_event_templates")
    op.drop_table("date_event_templates")
