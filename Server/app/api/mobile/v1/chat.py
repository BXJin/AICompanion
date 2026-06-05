from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

from app.dependencies import CurrentUserDep, DbSessionDep
from app.schemas.chat import AiriReplyView, ChatTurnRequest, ChatTurnResponse, MemoryFeedbackView, RelationshipFeedbackView
from app.services.chat_turn_service import ChatTurnCommand, ChatTurnService
from app.services.quota_service import QuotaExceededError

router = APIRouter(prefix="/chat", tags=["mobile-chat"])


@router.post("/turn", response_model=ChatTurnResponse)
async def create_chat_turn(
    request: ChatTurnRequest,
    current_user: CurrentUserDep,
    db: DbSessionDep,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ChatTurnResponse:
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Idempotency-Key header")

    try:
        result = await ChatTurnService(db).create_turn(
            ChatTurnCommand(
                user_id=current_user.user_id,
                character_id=request.character_id,
                conversation_id=request.conversation_id,
                input_text=request.input.text,
            )
        )
    except QuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ChatTurnResponse(
        conversation_id=result.conversation_id,
        message_id=result.user_message_id,
        reply=AiriReplyView(
            message_id=result.reply.message_id,
            text=result.reply.text,
            emotion=result.reply.emotion,
            intent=result.reply.intent,
        ),
        relationship_feedback=(
            RelationshipFeedbackView(
                changed=result.relationship_feedback.changed,
                summary=result.relationship_feedback.summary,
                event_id=result.relationship_feedback.event_id,
            )
            if result.relationship_feedback is not None
            else None
        ),
        memory_feedback=(
            MemoryFeedbackView(
                candidate_created=result.memory_feedback.candidate_created,
                summary=result.memory_feedback.summary,
                memory_id=result.memory_feedback.memory_id,
                extraction_job_id=result.memory_feedback.extraction_job_id,
            )
            if result.memory_feedback is not None
            else None
        ),
        date_suggestion=None,
        tts_job=None,
    )
