from sqlalchemy.orm import Session

from app.models.domain import CharacterRelationshipSnapshot


class RelationshipRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add_snapshot(self, snapshot: CharacterRelationshipSnapshot) -> CharacterRelationshipSnapshot:
        self._db.add(snapshot)
        return snapshot

    def get_snapshot(self, *, user_id: str, character_id: str) -> CharacterRelationshipSnapshot | None:
        return self._db.get(
            CharacterRelationshipSnapshot,
            {"user_id": user_id, "character_id": character_id},
        )
