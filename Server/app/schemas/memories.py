from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MemoryView(BaseModel):
    memory_id: str
    character_id: str
    memory_type: str
    summary: str
    status: Literal["candidate", "active", "hidden", "deleted", "rejected"]
    importance: int
    source_message_id: str | None
    created_at: datetime
    last_used_at: datetime | None
    deleted_at: datetime | None


class MemoryListResponse(BaseModel):
    items: list[MemoryView]


class MemoryMutationResponse(BaseModel):
    memory: MemoryView


class MemoryExtractionJobView(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed", "cancelled", "dead_letter"]


class MemoryExtractionJobResponse(BaseModel):
    job: MemoryExtractionJobView


class MemoryListQuery(BaseModel):
    character_id: str = "airi"
    status: Literal["candidate", "active", "hidden", "rejected"] | None = "active"
    limit: int = Field(default=50, ge=1, le=100)
