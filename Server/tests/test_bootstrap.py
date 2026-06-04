from fastapi.testclient import TestClient


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
    assert payload["character"]["character_id"] == "airi"
    assert payload["relationship"]["level"] == 1
    assert payload["unread_reward_count"] == 0
