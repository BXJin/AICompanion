from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Character


class CharacterRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, character: Character) -> Character:
        self._db.add(character)
        return character

    def get(self, character_id: str) -> Character | None:
        return self._db.get(Character, character_id)

    def get_by_slug(self, slug: str) -> Character | None:
        statement = select(Character).where(Character.slug == slug)
        return self._db.execute(statement).scalar_one_or_none()
