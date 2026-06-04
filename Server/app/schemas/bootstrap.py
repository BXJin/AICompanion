from pydantic import BaseModel, Field


class CharacterSummaryView(BaseModel):
    character_id: str
    display_name: str
    profile_version: str


class RelationshipSummaryView(BaseModel):
    level: int = Field(ge=1)
    affinity: int
    trust: int
    mood: str


class AppBootstrapResponse(BaseModel):
    character: CharacterSummaryView
    relationship: RelationshipSummaryView
    available_date_events: list[dict[str, object]]
    unread_reward_count: int = Field(ge=0)

