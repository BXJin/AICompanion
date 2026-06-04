from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import CharacterRelationshipSnapshot, RelationshipEvent
from app.repositories.relationships import RelationshipRepository


@dataclass(frozen=True)
class RelationshipDelta:
    affinity: int = 0
    trust: int = 0
    familiarity: int = 0


@dataclass(frozen=True)
class RelationshipApplyResult:
    changed: bool
    summary: str | None
    event_id: str | None
    snapshot: CharacterRelationshipSnapshot


class RelationshipStateService:
    def __init__(self, db: Session) -> None:
        self._relationships = RelationshipRepository(db)

    def apply_chat_event(
        self,
        *,
        user_id: str,
        character_id: str,
        source_message_id: str,
        event_type: str,
        delta: RelationshipDelta,
    ) -> RelationshipApplyResult:
        snapshot = self._relationships.get_snapshot(user_id=user_id, character_id=character_id)
        if snapshot is None:
            snapshot = self._relationships.add_snapshot(
                CharacterRelationshipSnapshot(
                    user_id=user_id,
                    character_id=character_id,
                    relationship_level=1,
                    affinity=10,
                    trust=5,
                    familiarity=0,
                    mood="warm",
                    updated_at=datetime.now(UTC),
                )
            )

        if event_type == "first_chat_completed":
            existing = self._relationships.get_event_by_type(
                user_id=user_id,
                character_id=character_id,
                event_type=event_type,
            )
            if existing is not None:
                return RelationshipApplyResult(changed=False, summary=None, event_id=None, snapshot=snapshot)

        event = self._relationships.add_event(
            RelationshipEvent(
                id=str(uuid4()),
                user_id=user_id,
                character_id=character_id,
                source_type="chat",
                source_id=source_message_id,
                affinity_delta=delta.affinity,
                trust_delta=delta.trust,
                familiarity_delta=delta.familiarity,
                metadata_json={"event_type": event_type},
                created_at=datetime.now(UTC),
            )
        )
        snapshot.affinity = self._clamp(snapshot.affinity + delta.affinity)
        snapshot.trust = self._clamp(snapshot.trust + delta.trust)
        snapshot.familiarity = self._clamp(snapshot.familiarity + delta.familiarity)
        snapshot.relationship_level = self._calculate_level(snapshot)
        snapshot.updated_at = datetime.now(UTC)
        return RelationshipApplyResult(
            changed=True,
            summary=self._format_summary(delta),
            event_id=event.id,
            snapshot=snapshot,
        )

    def _calculate_level(self, snapshot: CharacterRelationshipSnapshot) -> int:
        score = snapshot.affinity + snapshot.trust + snapshot.familiarity
        thresholds = [0, 20, 45, 75, 110, 150, 195, 245, 300, 360]
        level = 1
        for index, threshold in enumerate(thresholds, start=1):
            if score >= threshold:
                level = index
        return min(level, 10)

    def _format_summary(self, delta: RelationshipDelta) -> str:
        parts: list[str] = []
        if delta.affinity:
            parts.append(f"Affinity +{delta.affinity}")
        if delta.trust:
            parts.append(f"Trust +{delta.trust}")
        if delta.familiarity:
            parts.append(f"Familiarity +{delta.familiarity}")
        return ", ".join(parts)

    def _clamp(self, value: int) -> int:
        return max(0, min(100, value))
