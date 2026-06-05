from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CurrentUserDep, DbSessionDep
from app.schemas.memories import MemoryListResponse, MemoryMutationResponse, MemoryView
from app.services.memory_service import MemoryService, MemoryViewResult

router = APIRouter(prefix="/memories", tags=["mobile-memories"])


@router.get("", response_model=MemoryListResponse)
async def list_memories(
    current_user: CurrentUserDep,
    db: DbSessionDep,
    character_id: Annotated[str, Query(alias="characterId")] = "airi",
    memory_status: Annotated[
        Literal["candidate", "active", "hidden", "rejected"] | None,
        Query(alias="status"),
    ] = "active",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> MemoryListResponse:
    memories = MemoryService(db).list_memories(
        user_id=current_user.user_id,
        character_id=character_id,
        status=memory_status,
        limit=limit,
    )
    return MemoryListResponse(items=[_to_memory_view(memory) for memory in memories])


@router.post("/{memory_id}/activate", response_model=MemoryMutationResponse)
async def activate_memory(
    memory_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> MemoryMutationResponse:
    try:
        memory = MemoryService(db).activate_candidate(user_id=current_user.user_id, memory_id=memory_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MemoryMutationResponse(memory=_to_memory_view(memory))


@router.delete("/{memory_id}", response_model=MemoryMutationResponse)
async def delete_memory(
    memory_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
) -> MemoryMutationResponse:
    try:
        memory = MemoryService(db).delete_memory(user_id=current_user.user_id, memory_id=memory_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MemoryMutationResponse(memory=_to_memory_view(memory))


def _to_memory_view(memory: MemoryViewResult) -> MemoryView:
    return MemoryView(
        memory_id=memory.memory_id,
        character_id=memory.character_id,
        memory_type=memory.memory_type,
        summary=memory.summary,
        status=memory.status,  # type: ignore[arg-type]
        importance=memory.importance,
        source_message_id=memory.source_message_id,
        created_at=memory.created_at,
        last_used_at=memory.last_used_at,
        deleted_at=memory.deleted_at,
    )
