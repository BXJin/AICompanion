from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, user: User) -> User:
        self._db.add(user)
        return user

    def get(self, user_id: str) -> User | None:
        return self._db.get(User, user_id)

