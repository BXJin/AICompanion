from sqlalchemy.orm import Session

from app.models.domain import ProviderUsageEvent


class ProviderUsageRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, event: ProviderUsageEvent) -> ProviderUsageEvent:
        self._db.add(event)
        return event

    def get(self, event_id: str) -> ProviderUsageEvent | None:
        return self._db.get(ProviderUsageEvent, event_id)
