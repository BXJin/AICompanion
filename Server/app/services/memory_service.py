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
    extraction_job_id: str | None = None


@dataclass(frozen=True)
class MemoryViewResult:
    memory_id: str
    character_id: str
    memory_type: str
    summary: str
    status: str
    importance: int
    source_message_id: str | None
    created_at: datetime
    last_used_at: datetime | None
    deleted_at: datetime | None


class MemoryService:
    def __init__(self, db: Session) -> None:
        self._db = db
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

    def list_memories(
        self,
        *,
        user_id: str,
        character_id: str,
        status: str | None = "active",
        limit: int = 50,
    ) -> list[MemoryViewResult]:
        memories = self._memories.list_for_character(
            user_id=user_id,
            character_id=character_id,
            status=status,
            limit=limit,
        )
        return [self._to_view(memory) for memory in memories]

    def activate_candidate(self, *, user_id: str, memory_id: str) -> MemoryViewResult:
        memory = self._memories.get_for_user(user_id=user_id, memory_id=memory_id)
        if memory is None:
            raise ValueError("Memory was not found")
        if memory.status == "deleted":
            raise ValueError("Deleted memory cannot be activated")
        if memory.status not in {"candidate", "active"}:
            raise ValueError("Only candidate memories can be activated")
        memory.status = "active"
        memory.deleted_at = None
        self._db.commit()
        self._db.refresh(memory)
        return self._to_view(memory)

    def delete_memory(self, *, user_id: str, memory_id: str) -> MemoryViewResult:
        memory = self._memories.get_for_user(user_id=user_id, memory_id=memory_id)
        if memory is None:
            raise ValueError("Memory was not found")
        if memory.status != "deleted":
            memory.status = "deleted"
            memory.deleted_at = datetime.now(UTC)
            self._db.commit()
            self._db.refresh(memory)
        return self._to_view(memory)

    def retrieve_context(self, *, user_id: str, character_id: str, limit: int = 3) -> list[MemoryViewResult]:
        memories = self._memories.list_active_for_character(
            user_id=user_id,
            character_id=character_id,
            limit=limit,
        )
        return [self._to_view(memory) for memory in memories]

    def _extract_preference_summary(self, text: str) -> str | None:
        normalized = " ".join(text.strip().split())
        if len(normalized) < 4:
            return None

        lowered = normalized.lower()
        preference_markers = ("i like ", "i love ", "i prefer ", "좋아", "선호")
        if not any(marker in lowered for marker in preference_markers):
            return None

        return f"User shared a preference: {normalized[:160]}"

    def _to_view(self, memory: Memory) -> MemoryViewResult:
        return MemoryViewResult(
            memory_id=memory.id,
            character_id=memory.character_id,
            memory_type=memory.memory_type,
            summary=memory.summary,
            status=memory.status,
            importance=memory.importance,
            source_message_id=memory.source_message_id,
            created_at=memory.created_at,
            last_used_at=memory.last_used_at,
            deleted_at=memory.deleted_at,
        )
