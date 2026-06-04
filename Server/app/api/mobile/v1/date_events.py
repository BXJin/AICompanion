from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

from app.dependencies import CurrentUserDep, DbSessionDep
from app.schemas.date_events import (
    DateEventListResponse,
    DateEventView,
    DateFinishRequest,
    DateFinishResponse,
    DateMoveRequest,
    DateMoveResponse,
    DateStepChoiceView,
    DateStepView,
    RelationshipEventView,
    RewardEventView,
    StartDateEventResponse,
)
from app.services.date_event_service import DateEventService
from app.services.quota_service import QuotaExceededError

router = APIRouter(prefix="/date-events", tags=["mobile-date-events"])


@router.get("", response_model=DateEventListResponse)
async def list_date_events(current_user: CurrentUserDep, db: DbSessionDep) -> DateEventListResponse:
    events = DateEventService(db).list_events()
    return DateEventListResponse(
        items=[
            DateEventView(
                id=event.event_id,
                title=event.title,
                estimated_minutes=event.estimated_minutes,
                status=event.status,
                reward_preview=event.reward_preview,
                entry_cost=event.entry_cost,
            )
            for event in events
        ]
    )


@router.post("/{event_id}/start", response_model=StartDateEventResponse)
async def start_date_event(
    event_id: str,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> StartDateEventResponse:
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Idempotency-Key header")
    try:
        result = DateEventService(db).start(user_id=current_user.user_id, event_code=event_id, idempotency_key=idempotency_key)
    except QuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return StartDateEventResponse(session_id=result.session_id, event_id=result.event_id, step=_step_view(result.step))


@router.post("/{event_id}/move", response_model=DateMoveResponse)
async def move_date_event(
    event_id: str,
    request: DateMoveRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DateMoveResponse:
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Idempotency-Key header")
    try:
        result = DateEventService(db).move(
            user_id=current_user.user_id,
            session_id=request.session_id,
            sequence_no=request.sequence_no,
            choice_id=request.choice_id,
            idempotency_key=idempotency_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DateMoveResponse(
        session_id=result.session_id,
        status=result.status,
        step=_step_view(result.step) if result.step is not None else None,
        partial_feedback=result.partial_feedback,
    )


@router.post("/{event_id}/finish", response_model=DateFinishResponse)
async def finish_date_event(event_id: str, request: DateFinishRequest, current_user: CurrentUserDep, db: DbSessionDep) -> DateFinishResponse:
    try:
        result = DateEventService(db).finish(user_id=current_user.user_id, session_id=request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DateFinishResponse(
        session_id=result.session_id,
        result=result.result,
        score=result.score,
        airi_reaction=result.airi_reaction,
        relationship_event=RelationshipEventView(id=result.relationship_event_id, summary=result.relationship_summary),
        reward=RewardEventView(event_id=result.reward_event_id, status=result.reward_status, type=result.reward_type),
        memory_job_id=None,
    )


def _step_view(step) -> DateStepView:  # type: ignore[no-untyped-def]
    return DateStepView(
        sequence_no=step.sequence_no,
        airi_line=step.airi_line,
        choices=[DateStepChoiceView(choice_id=choice.choice_id, label=choice.label) for choice in step.choices],
    )
