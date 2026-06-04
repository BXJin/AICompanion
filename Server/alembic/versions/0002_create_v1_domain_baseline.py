"""create v1 domain baseline

Revision ID: 0002_create_v1_domain_baseline
Revises: 0001_create_users_and_sessions
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_create_v1_domain_baseline"
down_revision = "0001_create_users_and_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("profile_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_character_id", "conversations", ["character_id"])
    op.create_index("ix_conversations_user_character_last_message", "conversations", ["user_id", "character_id", "last_message_at"])
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("conversation_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_usage_event_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_character_id", "messages", ["character_id"])
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_user_created", "messages", ["user_id", "created_at"])
    op.create_index("ix_messages_user_id", "messages", ["user_id"])
    op.create_table(
        "character_relationship_snapshots",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("relationship_level", sa.Integer(), nullable=False),
        sa.Column("affinity", sa.Integer(), nullable=False),
        sa.Column("trust", sa.Integer(), nullable=False),
        sa.Column("familiarity", sa.Integer(), nullable=False),
        sa.Column("mood", sa.String(length=32), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "character_id"),
    )
    op.create_table(
        "relationship_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("affinity_delta", sa.Integer(), nullable=False),
        sa.Column("trust_delta", sa.Integer(), nullable=False),
        sa.Column("familiarity_delta", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_relationship_events_character_id", "relationship_events", ["character_id"])
    op.create_index("ix_relationship_events_user_character_created", "relationship_events", ["user_id", "character_id", "created_at"])
    op.create_index("ix_relationship_events_user_id", "relationship_events", ["user_id"])
    op.create_table(
        "memories",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("character_id", sa.String(length=64), nullable=False),
        sa.Column("memory_type", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False),
        sa.Column("source_message_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["source_message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memories_character_id", "memories", ["character_id"])
    op.create_index("ix_memories_user_character_last_used", "memories", ["user_id", "character_id", "last_used_at"])
    op.create_index("ix_memories_user_character_status_importance", "memories", ["user_id", "character_id", "status", "importance"])
    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_table(
        "credit_ledger",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("bucket", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("balance_after", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_ledger_user_bucket_created", "credit_ledger", ["user_id", "bucket", "created_at"])
    op.create_index("ix_credit_ledger_user_created", "credit_ledger", ["user_id", "created_at"])
    op.create_index("ix_credit_ledger_user_id", "credit_ledger", ["user_id"])
    op.create_index("ux_credit_ledger_idempotency_key", "credit_ledger", ["idempotency_key"], unique=True)
    op.create_table(
        "provider_usage_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("feature_route", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_units", sa.Integer(), nullable=False),
        sa.Column("output_units", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Numeric(12, 6), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_provider_usage_events_user_id", "provider_usage_events", ["user_id"])
    op.create_index("ix_provider_usage_provider_model_created", "provider_usage_events", ["provider", "model", "created_at"])
    op.create_index("ix_provider_usage_route_created", "provider_usage_events", ["feature_route", "created_at"])
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("admin_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_admin_audit_logs_admin_created", "admin_audit_logs", ["admin_id", "created_at"])
    op.create_index("ix_admin_audit_logs_target_created", "admin_audit_logs", ["target_type", "target_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_logs_target_created", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_admin_created", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
    op.drop_index("ix_provider_usage_route_created", table_name="provider_usage_events")
    op.drop_index("ix_provider_usage_provider_model_created", table_name="provider_usage_events")
    op.drop_index("ix_provider_usage_events_user_id", table_name="provider_usage_events")
    op.drop_table("provider_usage_events")
    op.drop_index("ix_credit_ledger_user_id", table_name="credit_ledger")
    op.drop_index("ux_credit_ledger_idempotency_key", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_user_created", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_user_bucket_created", table_name="credit_ledger")
    op.drop_table("credit_ledger")
    op.drop_index("ix_memories_user_id", table_name="memories")
    op.drop_index("ix_memories_user_character_status_importance", table_name="memories")
    op.drop_index("ix_memories_user_character_last_used", table_name="memories")
    op.drop_index("ix_memories_character_id", table_name="memories")
    op.drop_table("memories")
    op.drop_index("ix_relationship_events_user_id", table_name="relationship_events")
    op.drop_index("ix_relationship_events_user_character_created", table_name="relationship_events")
    op.drop_index("ix_relationship_events_character_id", table_name="relationship_events")
    op.drop_table("relationship_events")
    op.drop_table("character_relationship_snapshots")
    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_index("ix_messages_user_created", table_name="messages")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_index("ix_messages_conversation_created", table_name="messages")
    op.drop_index("ix_messages_character_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_user_id", table_name="conversations")
    op.drop_index("ix_conversations_user_character_last_message", table_name="conversations")
    op.drop_index("ix_conversations_character_id", table_name="conversations")
    op.drop_table("conversations")
    op.drop_table("characters")
