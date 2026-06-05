from fastapi.testclient import TestClient

from app.database import create_session
from app.models.user import User, UserSession
from app.repositories.user_sessions import UserSessionRepository


def test_guest_session_can_be_created(client: TestClient) -> None:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": "device-1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "Bearer"
    assert payload["access_token"].startswith("guest:")
    assert payload["refresh_token"].startswith("refresh:")
    assert payload["user_id"].startswith("guest_")


def test_guest_session_is_persisted(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": "device-1"})
    payload = response.json()

    db = create_session(test_settings)
    try:
        assert db.get(User, payload["user_id"]) is not None
        persisted_session = db.get(UserSession, payload["session_id"])
        assert persisted_session is not None
        assert persisted_session.device_id == "device-1"
        assert UserSessionRepository(db).is_active_session(
            user_id=payload["user_id"],
            session_id=payload["session_id"],
        )
    finally:
        db.close()


def test_non_guest_auth_is_not_implemented_in_skeleton(client: TestClient) -> None:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "apple"})

    assert response.status_code == 501


def test_admin_route_requires_admin_token(client: TestClient) -> None:
    response = client.get("/api/admin/v1/users/me")

    assert response.status_code == 401


def test_admin_route_accepts_admin_token(client: TestClient) -> None:
    response = client.get("/api/admin/v1/users/me", headers={"Authorization": "Bearer local-admin-token"})

    assert response.status_code == 200
    assert response.json()["boundary"] == "admin"


def test_billing_webhook_requires_signature(client: TestClient) -> None:
    response = client.post("/api/webhooks/v1/billing/google-play")

    assert response.status_code == 401


def test_billing_webhook_accepts_signature(client: TestClient) -> None:
    response = client.post(
        "/api/webhooks/v1/billing/google-play",
        headers={"X-Webhook-Signature": "local-webhook-secret", "X-Webhook-Event-ID": "evt-1"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted", "provider": "google_play", "event_id": "evt-1"}


def test_openapi_exposes_separate_api_boundaries(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/mobile/v1/auth/session" in paths
    assert "/api/mobile/v1/app/bootstrap" in paths
    assert "/api/mobile/v1/chat/turn" in paths
    assert "/api/mobile/v1/date-events" in paths
    assert "/api/mobile/v1/date-events/{event_id}/start" in paths
    assert "/api/mobile/v1/memories" in paths
    assert "/api/mobile/v1/memories/{memory_id}/activate" in paths
    assert "/api/admin/v1/users/me" in paths
    assert "/api/webhooks/v1/billing/google-play" in paths
    assert "/api/webhooks/v1/billing/apple" in paths
