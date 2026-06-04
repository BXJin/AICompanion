from fastapi import APIRouter

from app.dependencies import CurrentUserDep
from app.schemas.bootstrap import AppBootstrapResponse, CharacterSummaryView, RelationshipSummaryView

router = APIRouter(prefix="/app", tags=["mobile-app"])


@router.get("/bootstrap", response_model=AppBootstrapResponse)
async def bootstrap(current_user: CurrentUserDep) -> AppBootstrapResponse:
    return AppBootstrapResponse(
        character=CharacterSummaryView(
            character_id="airi",
            display_name="Airi",
            profile_version="airi-v1",
        ),
        relationship=RelationshipSummaryView(
            level=1,
            affinity=0,
            trust=0,
            mood="warm",
        ),
        available_date_events=[],
        unread_reward_count=0,
    )
