from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User, UserSession
from app.repositories.user_sessions import UserSessionRepository
from app.repositories.users import UserRepository
from app.security.auth import issue_guest_tokens


class AuthSessionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._sessions = UserSessionRepository(db)

    def create_guest_session(
        self,
        *,
        device_id: str | None,
        access_ttl_seconds: int,
        refresh_ttl_seconds: int,
    ) -> dict[str, object]:
        now = datetime.now(UTC)
        user_id = f"guest_{uuid4()}"
        session_id = str(uuid4())

        tokens = issue_guest_tokens(
            user_id=user_id,
            session_id=session_id,
            device_id=device_id,
            access_ttl_seconds=access_ttl_seconds,
            refresh_ttl_seconds=refresh_ttl_seconds,
        )

        self._users.add(
            User(
                id=user_id,
                auth_provider="guest",
                is_guest=True,
                status="active",
                created_at=now,
                updated_at=now,
            )
        )
        self._sessions.add(
            UserSession(
                id=session_id,
                user_id=user_id,
                device_id=device_id,
                refresh_token=str(tokens["refresh_token"]),
                status="active",
                created_at=now,
                expires_at=now + timedelta(seconds=access_ttl_seconds),
                refresh_expires_at=now + timedelta(seconds=refresh_ttl_seconds),
            )
        )
        self._db.commit()
        return tokens
