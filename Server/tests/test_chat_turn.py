from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import create_session
from app.models.domain import Character, CharacterRelationshipSnapshot, Conversation, Message


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
    assert payload["relationship_feedback"] is None
    assert payload["memory_feedback"] is None

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
        assert character is not None
        assert snapshot is not None
    finally:
        db.close()


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

    db = create_session(test_settings)
    try:
        messages = list(db.execute(select(Message).where(Message.conversation_id == conversation_id)).scalars())
        assert len(messages) == 4
    finally:
        db.close()
