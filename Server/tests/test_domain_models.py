from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import create_session
from app.models.base import Base
from app.models.domain import (
    AdminAuditLog,
    Character,
    CharacterRelationshipSnapshot,
    Conversation,
    CreditLedger,
    CreditBalanceSnapshot,
    Memory,
    Message,
    PlanAllowance,
    ProviderUsageEvent,
    QuotaCounter,
    RelationshipEvent,
)
from app.models.user import User


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4()}"


def test_domain_baseline_tables_are_registered() -> None:
    expected_tables = {
        "characters",
        "conversations",
        "messages",
        "character_relationship_snapshots",
        "relationship_events",
        "memories",
        "credit_ledger",
        "credit_balance_snapshots",
        "quota_counters",
        "plan_allowances",
        "provider_usage_events",
        "admin_audit_logs",
    }

    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


def test_credit_ledger_idempotency_key_is_unique() -> None:
    indexes = {index.name: index for index in CreditLedger.__table__.indexes}

    assert indexes["ux_credit_ledger_user_idempotency_key"].unique is True


def test_domain_baseline_models_can_be_persisted(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    db: Session = create_session(test_settings)
    now = datetime.now(UTC)
    user_id = _id("user")
    character_id = "airi"
    conversation_id = _id("conversation")
    message_id = _id("message")

    try:
        db.add(User(id=user_id, auth_provider="guest", is_guest=True, status="active", created_at=now, updated_at=now))
        db.add(
            Character(
                id=character_id,
                slug="airi",
                display_name="Airi",
                profile_version="airi-v1",
                status="active",
                created_at=now,
                updated_at=now,
            )
        )
        db.add(
            Conversation(
                id=conversation_id,
                user_id=user_id,
                character_id=character_id,
                status="active",
                title=None,
                created_at=now,
                last_message_at=now,
            )
        )
        db.add(
            Message(
                id=message_id,
                conversation_id=conversation_id,
                user_id=user_id,
                character_id=character_id,
                role="user",
                content_text="hello",
                status="visible",
                provider_usage_event_id=None,
                created_at=now,
            )
        )
        db.add(
            CharacterRelationshipSnapshot(
                user_id=user_id,
                character_id=character_id,
                relationship_level=1,
                affinity=0,
                trust=0,
                familiarity=0,
                mood="warm",
                updated_at=now,
            )
        )
        db.add(
            RelationshipEvent(
                id=_id("relationship_event"),
                user_id=user_id,
                character_id=character_id,
                source_type="chat",
                source_id=message_id,
                affinity_delta=1,
                trust_delta=0,
                familiarity_delta=1,
                metadata_json={},
                created_at=now,
            )
        )
        db.add(
            Memory(
                id=_id("memory"),
                user_id=user_id,
                character_id=character_id,
                memory_type="preference",
                summary="User likes calm greetings.",
                status="active",
                importance=2,
                source_message_id=message_id,
                created_at=now,
                last_used_at=None,
                deleted_at=None,
            )
        )
        db.add(
            CreditLedger(
                id=_id("credit"),
                user_id=user_id,
                bucket="free_daily",
                reason="initial_grant",
                delta=10,
                source_type="system",
                source_id=None,
                idempotency_key="initial-grant",
                balance_after=10,
                created_at=now,
                expires_at=None,
            )
        )
        db.add(
            ProviderUsageEvent(
                id=_id("provider_usage"),
                user_id=user_id,
                feature_route="default_chat",
                provider="mock",
                model="mock-default_chat",
                status="success",
                input_units=10,
                output_units=20,
                latency_ms=1,
                estimated_cost_usd=Decimal("0"),
                metadata_json={},
                created_at=now,
            )
        )
        db.add(
            AdminAuditLog(
                id=_id("audit"),
                admin_id="local-admin",
                action="seed_check",
                target_type="user",
                target_id=user_id,
                reason="test",
                metadata_json={},
                created_at=now,
            )
        )
        db.commit()

        assert db.get(Character, character_id) is not None
        assert db.get(Conversation, conversation_id) is not None
        assert db.get(Message, message_id) is not None
        assert db.get(CharacterRelationshipSnapshot, {"user_id": user_id, "character_id": character_id}) is not None
    finally:
        db.close()
