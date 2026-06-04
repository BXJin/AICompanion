from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUserDep, DbSessionDep
from app.schemas.bootstrap import (
    AppBootstrapResponse,
    BootstrapUserView,
    CharacterSummaryView,
    DailySummaryView,
    QuotaSummaryView,
    RelationshipSummaryView,
)
from app.services.app_bootstrap_service import AppBootstrapService

router = APIRouter(prefix="/app", tags=["mobile-app"])


@router.get("/bootstrap", response_model=AppBootstrapResponse)
async def bootstrap(current_user: CurrentUserDep, db: DbSessionDep) -> AppBootstrapResponse:
    try:
        result = AppBootstrapService(db).get_bootstrap(user_id=current_user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return AppBootstrapResponse(
        user=BootstrapUserView(
            user_id=result.user.user_id,
            plan=result.user.plan,
            age_gate_status=result.user.age_gate_status,
        ),
        character=CharacterSummaryView(
            character_id=result.character.character_id,
            display_name=result.character.display_name,
            profile_version=result.character.profile_version,
            status=result.character.status,
        ),
        relationship=RelationshipSummaryView(
            level=result.relationship.level,
            affinity=result.relationship.affinity,
            trust=result.relationship.trust,
            familiarity=result.relationship.familiarity,
            mood=result.relationship.mood,
            next_unlock_hint=result.relationship.next_unlock_hint,
        ),
        quota=QuotaSummaryView(
            text_turns_remaining=result.quota.text_turns_remaining,
            voice_seconds_remaining=result.quota.voice_seconds_remaining,
            tts_replies_remaining=result.quota.tts_replies_remaining,
            image_rewards_remaining=result.quota.image_rewards_remaining,
        ),
        daily=DailySummaryView(
            greeting=result.daily.greeting,
            date_hint=result.daily.date_hint,
            reward_hint=result.daily.reward_hint,
        ),
        available_date_events=result.available_date_events,
        unread_reward_count=result.unread_reward_count,
    )
