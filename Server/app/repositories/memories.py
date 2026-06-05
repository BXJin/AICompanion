from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Memory


class MemoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, memory: Memory) -> Memory:
        self._db.add(memory)
        return memory

    def get(self, memory_id: str) -> Memory | None:
        return self._db.get(Memory, memory_id)

    def get_for_user(self, *, user_id: str, memory_id: str) -> Memory | None:
        statement = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        return self._db.execute(statement).scalar_one_or_none()

    def list_for_character(
        self,
        *,
        user_id: str,
        character_id: str,
        status: str | None,
        limit: int = 50,
    ) -> list[Memory]:
        filters = [
            Memory.user_id == user_id,
            Memory.character_id == character_id,
            Memory.status != "deleted",
        ]
        if status is not None:
            filters.append(Memory.status == status)
        statement = (
            select(Memory)
            .where(*filters)
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        return list(self._db.execute(statement).scalars())

    def list_active_for_character(self, *, user_id: str, character_id: str, limit: int = 3) -> list[Memory]:
        statement = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.character_id == character_id,
                Memory.status == "active",
            )
            .order_by(Memory.importance.desc(), Memory.last_used_at.desc().nullslast(), Memory.created_at.desc())
            .limit(limit)
        )
        return list(self._db.execute(statement).scalars())
