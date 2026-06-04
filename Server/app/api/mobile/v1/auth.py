from fastapi import APIRouter, HTTPException, status

from app.dependencies import DbSessionDep, SettingsDep
from app.schemas.auth import AuthSessionRequest, AuthSessionResponse
from app.services.auth_session_service import AuthSessionService

router = APIRouter(prefix="/auth", tags=["mobile-auth"])


@router.post("/session", response_model=AuthSessionResponse)
async def create_session(request: AuthSessionRequest, settings: SettingsDep, db: DbSessionDep) -> AuthSessionResponse:
    if request.auth_provider != "guest":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Only guest auth is implemented in the skeleton",
        )

    tokens = AuthSessionService(db).create_guest_session(
        device_id=request.device_id,
        access_ttl_seconds=settings.access_token_ttl_seconds,
        refresh_ttl_seconds=settings.refresh_token_ttl_seconds,
    )
    return AuthSessionResponse(**tokens)
