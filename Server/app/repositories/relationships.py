from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import CharacterRelationshipSnapshot, RelationshipEvent


class RelationshipRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add_snapshot(self, snapshot: CharacterRelationshipSnapshot) -> CharacterRelationshipSnapshot:
        self._db.add(snapshot)
        return snapshot

    def add_event(self, event: RelationshipEvent) -> RelationshipEvent:
        self._db.add(event)
        return event

    def get_snapshot(self, *, user_id: str, character_id: str) -> CharacterRelationshipSnapshot | None:
        return self._db.get(
            CharacterRelationshipSnapshot,
            {"user_id": user_id, "character_id": character_id},
        )

    def get_event_by_type(self, *, user_id: str, character_id: str, event_type: str) -> RelationshipEvent | None:
        statement = (
            select(RelationshipEvent)
            .where(
                RelationshipEvent.user_id == user_id,
                RelationshipEvent.character_id == character_id,
                RelationshipEvent.metadata_json["event_type"].as_string() == event_type,
            )
            .order_by(RelationshipEvent.created_at.asc())
            .limit(1)
        )
        return self._db.execute(statement).scalar_one_or_none()
