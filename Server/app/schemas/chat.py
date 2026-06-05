from typing import Literal

from pydantic import BaseModel, Field


class ChatInput(BaseModel):
    type: Literal["text", "voice_transcript"] = "text"
    text: str = Field(min_length=1, max_length=4000)


class ChatClientContext(BaseModel):
    screen: Literal["chat", "date_result"] = "chat"
    local_time: str | None = None


class ChatTtsRequest(BaseModel):
    requested: bool = False
    style: Literal["warm", "soft", "playful", "careful"] | None = None


class ChatTurnRequest(BaseModel):
    character_id: str = "airi"
    conversation_id: str | None = None
    input: ChatInput
    client_context: ChatClientContext = Field(default_factory=ChatClientContext)
    tts: ChatTtsRequest | None = None


class AiriReplyView(BaseModel):
    message_id: str
    text: str
    emotion: Literal["warm", "playful", "concerned", "shy", "neutral"]
    intent: Literal["chat", "date_invite", "comfort", "memory_recall", "reward_hint", "fallback"]


class RelationshipFeedbackView(BaseModel):
    changed: bool
    summary: str | None
    event_id: str | None


class MemoryFeedbackView(BaseModel):
    candidate_created: bool
    summary: str | None
    memory_id: str | None = None
    extraction_job_id: str | None = None


class DateSuggestionView(BaseModel):
    event_id: str
    title: str


class ChatTurnResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply: AiriReplyView
    relationship_feedback: RelationshipFeedbackView | None
    memory_feedback: MemoryFeedbackView | None
    date_suggestion: DateSuggestionView | None
    tts_job: dict[str, object] | None
