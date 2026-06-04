from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import create_session
from app.models.domain import DateGameSession, GameMove, QuotaCounter, RelationshipEvent, RewardEvent


def _create_guest_session(client: TestClient) -> dict[str, object]:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": "device-date"})
    assert response.status_code == 200
    return response.json()


def _headers(session: dict[str, object], *, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def test_date_events_list_requires_auth(client: TestClient) -> None:
    response = client.get("/api/mobile/v1/date-events")

    assert response.status_code == 401


def test_date_event_start_move_finish_creates_rule_outputs(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client)

    list_response = client.get("/api/mobile/v1/date-events", headers=_headers(session))
    assert list_response.status_code == 200
    assert {item["id"] for item in list_response.json()["items"]} == {"comfort_date", "movie_talk", "weekend_plan"}

    start = client.post("/api/mobile/v1/date-events/movie_talk/start", headers=_headers(session, idempotency_key="date-start-1"))
    assert start.status_code == 200
    start_payload = start.json()
    assert start_payload["event_id"] == "movie_talk"
    assert start_payload["step"]["sequence_no"] == 1
    session_id = start_payload["session_id"]

    duplicate_start = client.post("/api/mobile/v1/date-events/movie_talk/start", headers=_headers(session, idempotency_key="date-start-1"))
    assert duplicate_start.status_code == 200
    assert duplicate_start.json()["session_id"] == session_id

    move_1 = client.post(
        "/api/mobile/v1/date-events/movie_talk/move",
        headers=_headers(session, idempotency_key="date-move-1"),
        json={"session_id": session_id, "sequence_no": 1, "choice_id": "cozy"},
    )
    assert move_1.status_code == 200
    assert move_1.json()["partial_feedback"] == {"score_delta": 15, "score": 15}
    assert move_1.json()["step"]["sequence_no"] == 2

    move_2 = client.post(
        "/api/mobile/v1/date-events/movie_talk/move",
        headers=_headers(session, idempotency_key="date-move-2"),
        json={"session_id": session_id, "sequence_no": 2, "choice_id": "cinema"},
    )
    assert move_2.status_code == 200
    assert move_2.json()["partial_feedback"] == {"score_delta": 15, "score": 30}
    assert move_2.json()["step"] is None

    finish = client.post(
        "/api/mobile/v1/date-events/movie_talk/finish",
        headers=_headers(session),
        json={"session_id": session_id},
    )
    assert finish.status_code == 200
    finish_payload = finish.json()
    assert finish_payload["result"] == "neutral"
    assert finish_payload["score"] == 30
    assert finish_payload["relationship_event"]["id"]
    assert finish_payload["reward"]["type"] == "note"
    assert finish_payload["reward"]["status"] == "unlocked"

    duplicate_finish = client.post(
        "/api/mobile/v1/date-events/movie_talk/finish",
        headers=_headers(session),
        json={"session_id": session_id},
    )
    assert duplicate_finish.status_code == 200
    assert duplicate_finish.json()["reward"]["event_id"] == finish_payload["reward"]["event_id"]

    db = create_session(test_settings)
    try:
        persisted_session = db.get(DateGameSession, session_id)
        moves = list(db.execute(select(GameMove).where(GameMove.session_id == session_id)).scalars())
        rewards = list(db.execute(select(RewardEvent).where(RewardEvent.source_id == session_id)).scalars())
        relationship_events = list(
            db.execute(
                select(RelationshipEvent).where(
                    RelationshipEvent.user_id == session["user_id"],
                    RelationshipEvent.source_id == session_id,
                )
            ).scalars()
        )
        quota_counter = db.query(QuotaCounter).filter_by(user_id=session["user_id"], feature="date_event").one()

        assert persisted_session is not None
        assert persisted_session.status == "completed"
        assert persisted_session.result == "neutral"
        assert persisted_session.score == 30
        assert len(moves) == 2
        assert len(rewards) == 1
        assert rewards[0].id == finish_payload["reward"]["event_id"]
        assert len(relationship_events) == 1
        assert relationship_events[0].metadata_json["event_type"] == "movie_talk_neutral"
        assert quota_counter.used_amount == 1
    finally:
        db.close()


def test_date_event_start_requires_idempotency_key(client: TestClient) -> None:
    session = _create_guest_session(client)

    response = client.post("/api/mobile/v1/date-events/movie_talk/start", headers=_headers(session))

    assert response.status_code == 400
