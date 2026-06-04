from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.domain import Character
from app.repositories.characters import CharacterRepository


AIRI_CHARACTER_ID = "airi"
AIRI_PROFILE_VERSION = "airi-v1"


class AiriSeedService:
    def __init__(self, db: Session) -> None:
        self._characters = CharacterRepository(db)

    def ensure_airi_character(self) -> Character:
        now = datetime.now(UTC)
        character = self._characters.get(AIRI_CHARACTER_ID)
        if character is not None:
            return character

        existing_by_slug = self._characters.get_by_slug(AIRI_CHARACTER_ID)
        if existing_by_slug is not None:
            return existing_by_slug

        return self._characters.add(
            Character(
                id=AIRI_CHARACTER_ID,
                slug=AIRI_CHARACTER_ID,
                display_name="Airi",
                profile_version=AIRI_PROFILE_VERSION,
                status="active",
                created_at=now,
                updated_at=now,
            )
        )
