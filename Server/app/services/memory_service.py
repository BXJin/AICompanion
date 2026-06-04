from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import Memory
from app.repositories.memories import MemoryRepository


@dataclass(frozen=True)
class MemoryCandidateResult:
    candidate_created: bool
    memory_id: str | None
    summary: str | None


class MemoryService:
    def __init__(self, db: Session) -> None:
        self._memories = MemoryRepository(db)

    def create_preference_candidate_from_chat(
        self,
        *,
        user_id: str,
        character_id: str,
        source_message_id: str,
        text: str,
    ) -> MemoryCandidateResult:
        summary = self._extract_preference_summary(text)
        if summary is None:
            return MemoryCandidateResult(candidate_created=False, memory_id=None, summary=None)

        memory = self._memories.add(
            Memory(
                id=str(uuid4()),
                user_id=user_id,
                character_id=character_id,
                memory_type="preference",
                summary=summary,
                status="candidate",
                importance=2,
                source_message_id=source_message_id,
                created_at=datetime.now(UTC),
                last_used_at=None,
                deleted_at=None,
            )
        )
        return MemoryCandidateResult(candidate_created=True, memory_id=memory.id, summary=summary)

    def _extract_preference_summary(self, text: str) -> str | None:
        normalized = " ".join(text.strip().split())
        if len(normalized) < 4:
            return None

        lowered = normalized.lower()
        preference_markers = ("i like ", "i love ", "i prefer ", "좋아", "선호")
        if not any(marker in lowered for marker in preference_markers):
            return None

        return f"User shared a preference: {normalized[:160]}"
