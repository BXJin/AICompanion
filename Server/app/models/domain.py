from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    profile_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="character")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    character: Mapped[Character] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="visible")
    provider_usage_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class CharacterRelationshipSnapshot(Base):
    __tablename__ = "character_relationship_snapshots"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    relationship_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    affinity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trust: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    familiarity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mood: Mapped[str] = mapped_column(String(32), nullable=False, default="warm")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class RelationshipEvent(Base):
    __tablename__ = "relationship_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    affinity_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trust_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    familiarity_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CreditLedger(Base):
    __tablename__ = "credit_ledger"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    bucket: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    balance_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CreditBalanceSnapshot(Base):
    __tablename__ = "credit_balance_snapshots"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bucket: Mapped[str] = mapped_column(String(32), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ledger_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class QuotaCounter(Base):
    __tablename__ = "quota_counters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False)
    feature: Mapped[str] = mapped_column(String(64), nullable=False)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    used_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    limit_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class PlanAllowance(Base):
    __tablename__ = "plan_allowances"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False)
    feature: Mapped[str] = mapped_column(String(64), nullable=False)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)
    limit_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class DateEventTemplate(Base):
    __tablename__ = "date_event_templates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_code: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    required_relationship_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    entry_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    reward_policy_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="public")
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class DateGameSession(Base):
    __tablename__ = "date_game_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    template_id: Mapped[str] = mapped_column(ForeignKey("date_event_templates.id"), nullable=False, index=True)
    template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    result: Mapped[str | None] = mapped_column(String(32), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    reward_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    relationship_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GameMove(Base):
    __tablename__ = "game_moves"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("date_game_sessions.id"), nullable=False, index=True)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    actor: Mapped[str] = mapped_column(String(32), nullable=False)
    move_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    rule_result_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class RewardEvent(Base):
    __tablename__ = "reward_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reward_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reward_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    rule_version: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class ProviderUsageEvent(Base):
    __tablename__ = "provider_usage_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    feature_route: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False, default=Decimal("0"))
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    admin_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


Index("ix_conversations_user_character_last_message", Conversation.user_id, Conversation.character_id, Conversation.last_message_at)
Index("ix_messages_conversation_created", Message.conversation_id, Message.created_at)
Index("ix_messages_user_created", Message.user_id, Message.created_at)
Index("ix_relationship_events_user_character_created", RelationshipEvent.user_id, RelationshipEvent.character_id, RelationshipEvent.created_at)
Index("ix_memories_user_character_status_importance", Memory.user_id, Memory.character_id, Memory.status, Memory.importance)
Index("ix_memories_user_character_last_used", Memory.user_id, Memory.character_id, Memory.last_used_at)
Index("ix_credit_ledger_user_created", CreditLedger.user_id, CreditLedger.created_at)
Index("ix_credit_ledger_user_bucket_created", CreditLedger.user_id, CreditLedger.bucket, CreditLedger.created_at)
Index("ux_credit_ledger_user_idempotency_key", CreditLedger.user_id, CreditLedger.idempotency_key, unique=True)
Index("ux_quota_counters_user_feature_period", QuotaCounter.user_id, QuotaCounter.feature, QuotaCounter.period_type, QuotaCounter.period_start, unique=True)
Index("ix_quota_counters_user_updated", QuotaCounter.user_id, QuotaCounter.updated_at)
Index("ux_plan_allowances_plan_feature_period_version", PlanAllowance.plan, PlanAllowance.feature, PlanAllowance.period_type, PlanAllowance.version, unique=True)
Index("ix_plan_allowances_enabled", PlanAllowance.enabled)
Index("ux_date_event_templates_code_version", DateEventTemplate.event_code, DateEventTemplate.version, unique=True)
Index("ix_date_event_templates_public", DateEventTemplate.enabled, DateEventTemplate.status)
Index("ix_date_game_sessions_user_character_started", DateGameSession.user_id, DateGameSession.character_id, DateGameSession.started_at)
Index("ix_date_game_sessions_user_status_started", DateGameSession.user_id, DateGameSession.status, DateGameSession.started_at)
Index("ux_date_game_sessions_user_idempotency_key", DateGameSession.user_id, DateGameSession.idempotency_key, unique=True)
Index("ux_game_moves_session_sequence", GameMove.session_id, GameMove.sequence_no, unique=True)
Index("ux_game_moves_session_idempotency_key", GameMove.session_id, GameMove.idempotency_key, unique=True)
Index("ix_reward_events_user_character_created", RewardEvent.user_id, RewardEvent.character_id, RewardEvent.created_at)
Index("ux_reward_events_source_reward", RewardEvent.user_id, RewardEvent.source_type, RewardEvent.source_id, RewardEvent.reward_type, unique=True)
Index("ix_provider_usage_route_created", ProviderUsageEvent.feature_route, ProviderUsageEvent.created_at)
Index("ix_provider_usage_provider_model_created", ProviderUsageEvent.provider, ProviderUsageEvent.model, ProviderUsageEvent.created_at)
Index("ix_admin_audit_logs_admin_created", AdminAuditLog.admin_id, AdminAuditLog.created_at)
Index("ix_admin_audit_logs_target_created", AdminAuditLog.target_type, AdminAuditLog.target_id, AdminAuditLog.created_at)
