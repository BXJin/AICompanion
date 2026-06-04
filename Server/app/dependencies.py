from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import session_scope
from app.repositories.user_sessions import UserSessionRepository
from app.security.auth import AdminUserContext, CurrentUserContext, parse_mobile_access_token


def get_request_settings(request: Request) -> Settings:
    return request.app.state.settings


SettingsDep = Annotated[Settings, Depends(get_request_settings)]


def get_db_session(settings: SettingsDep) -> Session:
    yield from session_scope(settings)


DbSessionDep = Annotated[Session, Depends(get_db_session)]


def get_current_user(
    db: DbSessionDep,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> CurrentUserContext:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization token")
    context = parse_mobile_access_token(authorization)
    if not UserSessionRepository(db).is_active_session(user_id=context.user_id, session_id=context.session_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired or unknown mobile session")
    return context


def get_admin_user(
    settings: SettingsDep,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> AdminUserContext:
    expected = f"Bearer {settings.admin_api_token}"
    if authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
    return AdminUserContext(admin_id="local-admin", roles=["super_admin"])


CurrentUserDep = Annotated[CurrentUserContext, Depends(get_current_user)]
AdminUserDep = Annotated[AdminUserContext, Depends(get_admin_user)]
