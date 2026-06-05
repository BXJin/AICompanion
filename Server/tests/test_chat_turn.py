from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import create_session
from app.models.domain import (
    Character,
    CharacterRelationshipSnapshot,
    Conversation,
    Memory,
    Message,
    AsyncJob,
    ProviderUsageEvent,
    QuotaCounter,
    RelationshipEvent,
)
from app.services.quota_service import QuotaService


def _create_guest_session(client: TestClient) -> dict[str, object]:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": "device-chat"})
    assert response.status_code == 200
    return response.json()


def _auth_headers(session: dict[str, object], *, idempotency_key: str | None = "chat-turn-1") -> dict[str, str]:
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def test_chat_turn_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/mobile/v1/chat/turn",
        headers={"Idempotency-Key": "chat-turn-1"},
        json={"character_id": "airi", "input": {"type": "text", "text": "hello"}},
    )

    assert response.status_code == 401


def test_chat_turn_requires_idempotency_key(client: TestClient) -> None:
    session = _create_guest_session(client)

    response = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_auth_headers(session, idempotency_key=None),
        json={"character_id": "airi", "input": {"type": "text", "text": "hello"}},
    )

    assert response.status_code == 400


def test_chat_turn_with_mock_provider_creates_conversation_and_messages(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client)

    response = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_auth_headers(session),
        json={"character_id": "airi", "input": {"type": "text", "text": "I like quiet movies."}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"]
    assert payload["message_id"]
    assert payload["reply"]["message_id"]
    assert payload["reply"]["emotion"] == "warm"
    assert payload["reply"]["intent"] == "chat"
    assert "I like quiet movies." in payload["reply"]["text"]
    assert payload["relationship_feedback"]["changed"] is True
    assert payload["relationship_feedback"]["summary"] == "Affinity +2, Familiarity +1, Familiarity +1"
    assert payload["relationship_feedback"]["event_id"]
    assert payload["memory_feedback"]["candidate_created"] is True
    assert payload["memory_feedback"]["summary"] == "User shared a preference: I like quiet movies."
    assert payload["memory_feedback"]["memory_id"]
    assert payload["memory_feedback"]["extraction_job_id"]

    db = create_session(test_settings)
    try:
        conversation = db.get(Conversation, payload["conversation_id"])
        user_message = db.get(Message, payload["message_id"])
        assistant_message = db.get(Message, payload["reply"]["message_id"])
        character = db.get(Character, "airi")
        snapshot = db.get(
            CharacterRelationshipSnapshot,
            {"user_id": session["user_id"], "character_id": "airi"},
        )

        assert conversation is not None
        assert conversation.user_id == session["user_id"]
        assert conversation.character_id == "airi"
        assert conversation.last_message_at is not None
        assert user_message is not None
        assert user_message.role == "user"
        assert user_message.content_text == "I like quiet movies."
        assert assistant_message is not None
        assert assistant_message.role == "assistant"
        assert assistant_message.conversation_id == conversation.id
        assert assistant_message.provider_usage_event_id is not None
        provider_usage = db.get(ProviderUsageEvent, assistant_message.provider_usage_event_id)
        assert provider_usage is not None
        assert provider_usage.user_id == session["user_id"]
        assert provider_usage.feature_route == "default_chat"
        assert provider_usage.provider == "mock"
        assert provider_usage.model == "mock-default_chat"
        assert provider_usage.status == "success"
        assert provider_usage.input_units == 10
        assert provider_usage.output_units == 18
        assert provider_usage.metadata_json == {"unit_type": "tokens"}
        assert character is not None
        assert snapshot is not None
        assert snapshot.affinity == 12
        assert snapshot.trust == 5
        assert snapshot.familiarity == 2
        relationship_events = list(
            db.execute(select(RelationshipEvent).where(RelationshipEvent.user_id == session["user_id"])).scalars()
        )
        memories = list(db.execute(select(Memory).where(Memory.user_id == session["user_id"])).scalars())
        quota_counter = db.query(QuotaCounter).filter_by(user_id=session["user_id"], feature="text_turn").one()
        extraction_job = db.get(AsyncJob, payload["memory_feedback"]["extraction_job_id"])
        assert [event.metadata_json["event_type"] for event in relationship_events] == [
            "first_chat_completed",
            "user_shared_preference",
        ]
        assert quota_counter.used_amount == 1
        assert quota_counter.limit_amount == 50
        assert len(memories) == 1
        assert memories[0].status == "candidate"
        assert memories[0].memory_type == "preference"
        assert memories[0].source_message_id == user_message.id
        assert extraction_job is not None
        assert extraction_job.job_type == "memory_extraction"
        assert extraction_job.status == "queued"
        assert extraction_job.source_id == user_message.id
        assert extraction_job.result_ref == memories[0].id
    finally:
        db.close()


def test_chat_turn_returns_429_when_text_turn_quota_is_exhausted(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client)
    db = create_session(test_settings)
    try:
        quota = QuotaService(db)
        quota.consume(user_id=session["user_id"], plan="free", feature="text_turn", amount=50)
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_auth_headers(session, idempotency_key="chat-turn-quota-exceeded"),
        json={"character_id": "airi", "input": {"type": "text", "text": "hello"}},
    )

    assert response.status_code == 429


def test_chat_turn_can_continue_existing_conversation(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client)
    first = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_auth_headers(session, idempotency_key="chat-turn-existing-1"),
        json={"character_id": "airi", "input": {"type": "text", "text": "first"}},
    )
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]

    second = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_auth_headers(session, idempotency_key="chat-turn-existing-2"),
        json={"character_id": "airi", "conversation_id": conversation_id, "input": {"type": "text", "text": "second"}},
    )

    assert second.status_code == 200
    assert second.json()["conversation_id"] == conversation_id
    assert second.json()["relationship_feedback"]["changed"] is False
    assert second.json()["memory_feedback"]["candidate_created"] is False

    db = create_session(test_settings)
    try:
        messages = list(db.execute(select(Message).where(Message.conversation_id == conversation_id)).scalars())
        events = list(db.execute(select(RelationshipEvent).where(RelationshipEvent.user_id == session["user_id"])).scalars())
        assert len(messages) == 4
        assert [event.metadata_json["event_type"] for event in events] == ["first_chat_completed"]
    finally:
        db.close()
