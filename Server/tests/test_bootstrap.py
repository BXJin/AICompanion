from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.database import create_session
from app.models.domain import Character, CharacterRelationshipSnapshot


def _create_guest_session(client: TestClient) -> dict[str, object]:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": "device-1"})
    assert response.status_code == 200
    return response.json()


def test_bootstrap_requires_auth(client: TestClient) -> None:
    response = client.get("/api/mobile/v1/app/bootstrap")

    assert response.status_code == 401


def test_bootstrap_returns_airi_state_for_authenticated_guest(client: TestClient) -> None:
    session = _create_guest_session(client)

    response = client.get(
        "/api/mobile/v1/app/bootstrap",
        headers={"Authorization": f"Bearer {session['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["user_id"] == session["user_id"]
    assert payload["user"]["plan"] == "free"
    assert payload["character"]["character_id"] == "airi"
    assert payload["character"]["display_name"] == "Airi"
    assert payload["character"]["profile_version"] == "airi-v1"
    assert payload["character"]["status"] == "active"
    assert payload["relationship"]["level"] == 1
    assert payload["relationship"]["affinity"] == 10
    assert payload["relationship"]["trust"] == 5
    assert payload["relationship"]["familiarity"] == 0
    assert payload["relationship"]["next_unlock_hint"] == "First Airi note"
    assert payload["quota"]["text_turns_remaining"] == 50
    assert payload["daily"]["date_hint"]["event_id"] == "movie_talk"
    assert payload["unread_reward_count"] == 0


def test_bootstrap_seeds_airi_and_initial_relationship_once(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client)
    headers = {"Authorization": f"Bearer {session['access_token']}"}

    first_response = client.get("/api/mobile/v1/app/bootstrap", headers=headers)
    second_response = client.get("/api/mobile/v1/app/bootstrap", headers=headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    db = create_session(test_settings)
    try:
        character = db.get(Character, "airi")
        snapshot = db.get(
            CharacterRelationshipSnapshot,
            {"user_id": session["user_id"], "character_id": "airi"},
        )
        character_count = db.execute(select(func.count()).select_from(Character).where(Character.id == "airi")).scalar_one()
        snapshot_count = db.execute(
            select(func.count())
            .select_from(CharacterRelationshipSnapshot)
            .where(
                CharacterRelationshipSnapshot.user_id == session["user_id"],
                CharacterRelationshipSnapshot.character_id == "airi",
            )
        ).scalar_one()

        assert character is not None
        assert character.slug == "airi"
        assert snapshot is not None
        assert snapshot.relationship_level == 1
        assert snapshot.affinity == 10
        assert character_count == 1
        assert snapshot_count == 1
    finally:
        db.close()
