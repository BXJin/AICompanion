from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import AsyncJob


class AsyncJobRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, job: AsyncJob) -> AsyncJob:
        self._db.add(job)
        return job

    def get(self, job_id: str) -> AsyncJob | None:
        return self._db.get(AsyncJob, job_id)

    def list_queued(self, *, job_type: str, limit: int = 20) -> list[AsyncJob]:
        statement = (
            select(AsyncJob)
            .where(AsyncJob.job_type == job_type, AsyncJob.status == "queued")
            .order_by(AsyncJob.priority.asc(), AsyncJob.created_at.asc())
            .limit(limit)
        )
        return list(self._db.execute(statement).scalars())
