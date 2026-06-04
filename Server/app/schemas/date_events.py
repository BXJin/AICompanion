from pydantic import BaseModel, Field


class DateEventView(BaseModel):
    id: str
    title: str
    estimated_minutes: int
    status: str
    reward_preview: dict[str, object]
    entry_cost: int


class DateEventListResponse(BaseModel):
    items: list[DateEventView]


class DateStepChoiceView(BaseModel):
    choice_id: str
    label: str


class DateStepView(BaseModel):
    sequence_no: int
    airi_line: str
    choices: list[DateStepChoiceView]


class StartDateEventResponse(BaseModel):
    session_id: str
    event_id: str
    step: DateStepView


class DateMoveRequest(BaseModel):
    session_id: str
    sequence_no: int = Field(ge=1)
    choice_id: str
    free_text: str | None = None


class DateFinishRequest(BaseModel):
    session_id: str


class DateMoveResponse(BaseModel):
    session_id: str
    status: str
    step: DateStepView | None
    partial_feedback: dict[str, object] | None


class RelationshipEventView(BaseModel):
    id: str | None
    summary: str | None


class RewardEventView(BaseModel):
    event_id: str | None
    status: str | None
    type: str | None


class DateFinishResponse(BaseModel):
    session_id: str
    result: str
    score: int
    airi_reaction: str
    relationship_event: RelationshipEventView
    reward: RewardEventView | None
    memory_job_id: str | None
