from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.domain import Character, CharacterRelationshipSnapshot
from app.models.user import User
from app.repositories.characters import CharacterRepository
from app.repositories.relationships import RelationshipRepository
from app.repositories.users import UserRepository


AIRI_CHARACTER_ID = "airi"
AIRI_PROFILE_VERSION = "airi-v1"


@dataclass(frozen=True)
class BootstrapUser:
    user_id: str
    plan: str
    age_gate_status: str


@dataclass(frozen=True)
class BootstrapCharacter:
    character_id: str
    display_name: str
    profile_version: str
    status: str


@dataclass(frozen=True)
class BootstrapRelationship:
    level: int
    affinity: int
    trust: int
    familiarity: int
    mood: str
    next_unlock_hint: str


@dataclass(frozen=True)
class BootstrapQuota:
    text_turns_remaining: int
    voice_seconds_remaining: int
    tts_replies_remaining: int
    image_rewards_remaining: int


@dataclass(frozen=True)
class BootstrapDaily:
    greeting: str
    date_hint: dict[str, object] | None
    reward_hint: dict[str, object] | None


@dataclass(frozen=True)
class AppBootstrapResult:
    user: BootstrapUser
    character: BootstrapCharacter
    relationship: BootstrapRelationship
    quota: BootstrapQuota
    daily: BootstrapDaily
    available_date_events: list[dict[str, object]]
    unread_reward_count: int


class AppBootstrapService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._characters = CharacterRepository(db)
        self._relationships = RelationshipRepository(db)

    def get_bootstrap(self, *, user_id: str) -> AppBootstrapResult:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError("Bootstrap requested for an unknown user")

        character = self._ensure_airi_character()
        relationship = self._ensure_initial_relationship(user=user, character=character)
        self._db.commit()

        return AppBootstrapResult(
            user=BootstrapUser(user_id=user.id, plan="free", age_gate_status="unknown"),
            character=BootstrapCharacter(
                character_id=character.id,
                display_name=character.display_name,
                profile_version=character.profile_version,
                status=character.status,
            ),
            relationship=BootstrapRelationship(
                level=relationship.relationship_level,
                affinity=relationship.affinity,
                trust=relationship.trust,
                familiarity=relationship.familiarity,
                mood=relationship.mood,
                next_unlock_hint="First Airi note",
            ),
            quota=BootstrapQuota(
                text_turns_remaining=50,
                voice_seconds_remaining=60,
                tts_replies_remaining=5,
                image_rewards_remaining=1,
            ),
            daily=BootstrapDaily(
                greeting="Airi is ready to chat.",
                date_hint={"event_id": "movie_talk", "title": "Movie talk date"},
                reward_hint={"type": "note", "title": "First Airi note"},
            ),
            available_date_events=[],
            unread_reward_count=0,
        )

    def _ensure_airi_character(self) -> Character:
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

    def _ensure_initial_relationship(self, *, user: User, character: Character) -> CharacterRelationshipSnapshot:
        snapshot = self._relationships.get_snapshot(user_id=user.id, character_id=character.id)
        if snapshot is not None:
            return snapshot

        return self._relationships.add_snapshot(
            CharacterRelationshipSnapshot(
                user_id=user.id,
                character_id=character.id,
                relationship_level=1,
                affinity=10,
                trust=5,
                familiarity=0,
                mood="warm",
                updated_at=datetime.now(UTC),
            )
        )
