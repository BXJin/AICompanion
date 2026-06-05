from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.repositories.async_jobs import AsyncJobRepository


@dataclass(frozen=True)
class MemoryExtractionWorkerResult:
    processed: int


class MemoryExtractionWorker:
    """Skeleton worker for future provider-backed memory extraction."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._jobs = AsyncJobRepository(db)

    def run_once(self, *, limit: int = 20) -> MemoryExtractionWorkerResult:
        jobs = self._jobs.list_queued(job_type="memory_extraction", limit=limit)
        now = datetime.now(UTC)
        for job in jobs:
            job.status = "succeeded"
            job.started_at = now
            job.finished_at = now
            job.attempts += 1
        self._db.commit()
        return MemoryExtractionWorkerResult(processed=len(jobs))
