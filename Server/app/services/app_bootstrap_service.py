from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.domain import Character, CharacterRelationshipSnapshot
from app.models.user import User
from app.repositories.relationships import RelationshipRepository
from app.repositories.users import UserRepository
from app.services.airi_seed_service import AiriSeedService
from app.services.quota_service import QuotaService


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
        self._relationships = RelationshipRepository(db)
        self._airi_seed = AiriSeedService(db)
        self._quota = QuotaService(db)

    def get_bootstrap(self, *, user_id: str) -> AppBootstrapResult:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError("Bootstrap requested for an unknown user")

        character = self._airi_seed.ensure_airi_character()
        relationship = self._ensure_initial_relationship(user=user, character=character)
        text_turn_quota = self._quota.remaining(user_id=user.id, plan="free", feature="text_turn")
        voice_quota = self._quota.remaining(user_id=user.id, plan="free", feature="voice_second")
        tts_quota = self._quota.remaining(user_id=user.id, plan="free", feature="tts_reply")
        image_quota = self._quota.remaining(user_id=user.id, plan="free", feature="image_reward")
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
                text_turns_remaining=text_turn_quota.remaining,
                voice_seconds_remaining=voice_quota.remaining,
                tts_replies_remaining=tts_quota.remaining,
                image_rewards_remaining=image_quota.remaining,
            ),
            daily=BootstrapDaily(
                greeting="Airi is ready to chat.",
                date_hint={"event_id": "movie_talk", "title": "Movie talk date"},
                reward_hint={"type": "note", "title": "First Airi note"},
            ),
            available_date_events=[],
            unread_reward_count=0,
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

    def ensure_initial_relationship(self, *, user_id: str, character: Character) -> CharacterRelationshipSnapshot:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError("Bootstrap requested for an unknown user")
        snapshot = self._ensure_initial_relationship(user=user, character=character)
        self._db.flush()
        return snapshot
