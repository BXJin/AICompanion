from pydantic import BaseModel, Field


class BootstrapUserView(BaseModel):
    user_id: str
    plan: str
    age_gate_status: str


class CharacterSummaryView(BaseModel):
    character_id: str
    display_name: str
    profile_version: str
    status: str


class RelationshipSummaryView(BaseModel):
    level: int = Field(ge=1)
    affinity: int
    trust: int
    familiarity: int
    mood: str
    next_unlock_hint: str


class QuotaSummaryView(BaseModel):
    text_turns_remaining: int = Field(ge=0)
    voice_seconds_remaining: int = Field(ge=0)
    tts_replies_remaining: int = Field(ge=0)
    image_rewards_remaining: int = Field(ge=0)


class DailySummaryView(BaseModel):
    greeting: str
    date_hint: dict[str, object] | None
    reward_hint: dict[str, object] | None


class AppBootstrapResponse(BaseModel):
    user: BootstrapUserView
    character: CharacterSummaryView
    relationship: RelationshipSummaryView
    quota: QuotaSummaryView
    daily: DailySummaryView
    available_date_events: list[dict[str, object]]
    unread_reward_count: int = Field(ge=0)
