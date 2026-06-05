from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import create_session
from app.models.domain import AsyncJob, Memory
from app.workers.memory_extraction_worker import MemoryExtractionWorker


def _create_guest_session(client: TestClient, *, device_id: str = "device-memory") -> dict[str, object]:
    response = client.post("/api/mobile/v1/auth/session", json={"auth_provider": "guest", "device_id": device_id})
    assert response.status_code == 200
    return response.json()


def _headers(session: dict[str, object], *, idempotency_key: str = "memory-chat-1") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {session['access_token']}",
        "Idempotency-Key": idempotency_key,
    }


def _create_memory_candidate(client: TestClient, session: dict[str, object]) -> str:
    response = client.post(
        "/api/mobile/v1/chat/turn",
        headers=_headers(session),
        json={"character_id": "airi", "input": {"type": "text", "text": "I like rainy playlists."}},
    )
    assert response.status_code == 200
    memory_id = response.json()["memory_feedback"]["memory_id"]
    assert memory_id
    return memory_id


def test_memory_routes_require_auth(client: TestClient) -> None:
    response = client.get("/api/mobile/v1/memories")

    assert response.status_code == 401


def test_memory_candidate_can_be_activated_listed_and_deleted(client: TestClient) -> None:
    session = _create_guest_session(client)
    memory_id = _create_memory_candidate(client, session)
    auth_headers = {"Authorization": f"Bearer {session['access_token']}"}

    active_before = client.get("/api/mobile/v1/memories?characterId=airi&status=active", headers=auth_headers)
    assert active_before.status_code == 200
    assert active_before.json()["items"] == []

    candidates = client.get("/api/mobile/v1/memories?characterId=airi&status=candidate", headers=auth_headers)
    assert candidates.status_code == 200
    assert [item["memory_id"] for item in candidates.json()["items"]] == [memory_id]

    activated = client.post(f"/api/mobile/v1/memories/{memory_id}/activate", headers=auth_headers)
    assert activated.status_code == 200
    assert activated.json()["memory"]["status"] == "active"

    active_after = client.get("/api/mobile/v1/memories?characterId=airi&status=active", headers=auth_headers)
    assert active_after.status_code == 200
    assert [item["memory_id"] for item in active_after.json()["items"]] == [memory_id]

    deleted = client.delete(f"/api/mobile/v1/memories/{memory_id}", headers=auth_headers)
    assert deleted.status_code == 200
    assert deleted.json()["memory"]["status"] == "deleted"
    assert deleted.json()["memory"]["deleted_at"] is not None

    active_after_delete = client.get("/api/mobile/v1/memories?characterId=airi&status=active", headers=auth_headers)
    assert active_after_delete.status_code == 200
    assert active_after_delete.json()["items"] == []


def test_deleted_memory_is_excluded_from_retrieval(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client, device_id="device-memory-retrieval")
    memory_id = _create_memory_candidate(client, session)
    auth_headers = {"Authorization": f"Bearer {session['access_token']}"}
    assert client.post(f"/api/mobile/v1/memories/{memory_id}/activate", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/mobile/v1/memories/{memory_id}", headers=auth_headers).status_code == 200

    db = create_session(test_settings)
    try:
        memories = list(
            db.execute(
                select(Memory).where(
                    Memory.user_id == session["user_id"],
                    Memory.character_id == "airi",
                    Memory.status == "active",
                )
            ).scalars()
        )
        assert memories == []
    finally:
        db.close()


def test_memory_extraction_job_skeleton_processes_queued_jobs(client: TestClient, test_settings) -> None:  # type: ignore[no-untyped-def]
    session = _create_guest_session(client, device_id="device-memory-worker")
    _create_memory_candidate(client, session)

    db = create_session(test_settings)
    try:
        job = db.execute(select(AsyncJob).where(AsyncJob.user_id == session["user_id"])).scalar_one()
        assert job.job_type == "memory_extraction"
        assert job.status == "queued"

        result = MemoryExtractionWorker(db).run_once()
        assert result.processed == 1
        db.refresh(job)
        assert job.status == "succeeded"
        assert job.started_at is not None
        assert job.finished_at is not None
        assert job.attempts == 1
    finally:
        db.close()
