from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass(frozen=True)
class CurrentUserContext:
    user_id: str
    device_id: str | None
    session_id: str
    is_guest: bool


@dataclass(frozen=True)
class AdminUserContext:
    admin_id: str
    roles: list[str]


def issue_guest_tokens(
    *,
    user_id: str,
    session_id: str,
    device_id: str | None,
    access_ttl_seconds: int,
    refresh_ttl_seconds: int,
) -> dict[str, object]:
    access_token = f"guest:{user_id}:{session_id}:{device_id or 'unknown'}"
    refresh_token = f"refresh:{user_id}:{session_id}"
    return {
        "user_id": user_id,
        "session_id": session_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": access_ttl_seconds,
        "refresh_expires_in": refresh_ttl_seconds,
    }


def parse_mobile_access_token(authorization: str) -> CurrentUserContext:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme")

    token = authorization.removeprefix(prefix)
    parts = token.split(":")
    if len(parts) != 4 or parts[0] != "guest":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid mobile token")

    _, user_id, session_id, device_id = parts
    return CurrentUserContext(
        user_id=user_id,
        session_id=session_id,
        device_id=None if device_id == "unknown" else device_id,
        is_guest=True,
    )
