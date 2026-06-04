from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserSession


class UserSessionRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, session: UserSession) -> UserSession:
        self._db.add(session)
        return session

    def get(self, session_id: str) -> UserSession | None:
        return self._db.get(UserSession, session_id)

    def is_active_session(self, *, user_id: str, session_id: str) -> bool:
        statement = select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id,
            UserSession.status == "active",
            UserSession.expires_at > datetime.now(UTC),
        )
        return self._db.execute(statement).scalar_one_or_none() is not None

