from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import AsyncJob
from app.repositories.async_jobs import AsyncJobRepository


@dataclass(frozen=True)
class AsyncJobCreateResult:
    job_id: str
    status: str


class AsyncJobService:
    def __init__(self, db: Session) -> None:
        self._jobs = AsyncJobRepository(db)

    def enqueue_memory_extraction(
        self,
        *,
        user_id: str,
        source_message_id: str,
        memory_id: str | None,
    ) -> AsyncJobCreateResult:
        job = self._jobs.add(
            AsyncJob(
                id=str(uuid4()),
                user_id=user_id,
                job_type="memory_extraction",
                status="queued",
                priority=100,
                attempts=0,
                provider=None,
                source_type="message",
                source_id=source_message_id,
                result_ref=memory_id,
                error_code=None,
                payload_json={"memory_id": memory_id} if memory_id is not None else {},
                created_at=datetime.now(UTC),
                started_at=None,
                finished_at=None,
            )
        )
        return AsyncJobCreateResult(job_id=job.id, status=job.status)
