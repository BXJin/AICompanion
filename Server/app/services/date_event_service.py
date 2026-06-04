from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import DateEventTemplate, DateGameSession, GameMove, RewardEvent
from app.repositories.date_events import DateEventRepository
from app.services.airi_seed_service import AIRI_CHARACTER_ID, AiriSeedService
from app.services.date_event_rule_engine import RULE_VERSION, DateEventRuleEngine, DateStep
from app.services.quota_service import QuotaService
from app.services.relationship_state_service import RelationshipStateService


DEFAULT_DATE_EVENTS = [
    ("movie_talk", "Movie talk date", 5, {"success": ["note", "image"], "neutral": ["note"]}),
    ("comfort_date", "Comfort date", 5, {"success": ["note", "voice"], "neutral": ["note"]}),
    ("weekend_plan", "Weekend plan", 5, {"success": ["note"], "neutral": ["note"]}),
]


@dataclass(frozen=True)
class DateEventViewResult:
    event_id: str
    title: str
    estimated_minutes: int
    status: str
    reward_preview: dict[str, object]
    entry_cost: int


@dataclass(frozen=True)
class DateStartResult:
    session_id: str
    event_id: str
    step: DateStep


@dataclass(frozen=True)
class DateMoveResult:
    session_id: str
    status: str
    step: DateStep | None
    partial_feedback: dict[str, object] | None


@dataclass(frozen=True)
class DateFinishResult:
    session_id: str
    result: str
    score: int
    airi_reaction: str
    relationship_event_id: str | None
    relationship_summary: str | None
    reward_event_id: str | None
    reward_status: str | None
    reward_type: str | None


class DateEventService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._dates = DateEventRepository(db)
        self._airi = AiriSeedService(db)
        self._quota = QuotaService(db)
        self._relationship = RelationshipStateService(db)
        self._rules = DateEventRuleEngine()

    def list_events(self) -> list[DateEventViewResult]:
        self.ensure_default_templates()
        return [
            DateEventViewResult(
                event_id=template.event_code,
                title=template.title,
                estimated_minutes=template.estimated_minutes,
                status="available",
                reward_preview=template.reward_policy_json,
                entry_cost=template.entry_cost,
            )
            for template in self._dates.list_public_templates()
        ]

    def start(self, *, user_id: str, event_code: str, idempotency_key: str) -> DateStartResult:
        existing = self._dates.get_session_by_idempotency_key(user_id=user_id, idempotency_key=idempotency_key)
        if existing is not None:
            template = self._get_template_by_id(existing.template_id)
            return DateStartResult(session_id=existing.id, event_id=template.event_code, step=self._rules.first_step(template.event_code))

        self.ensure_default_templates()
        template = self._dates.get_template_by_code(event_code)
        if template is None:
            raise ValueError("Date event was not found")
        character = self._airi.ensure_airi_character()
        self._quota.consume(user_id=user_id, plan="free", feature="date_event")
        first_step = self._rules.first_step(event_code)
        session = self._dates.add_session(
            DateGameSession(
                id=str(uuid4()),
                user_id=user_id,
                character_id=character.id,
                template_id=template.id,
                template_version=template.version,
                status="active",
                result=None,
                score=None,
                state_json={"event_code": event_code, "score": 0, "next_sequence_no": first_step.sequence_no},
                reward_event_id=None,
                relationship_event_id=None,
                idempotency_key=idempotency_key,
                started_at=datetime.now(UTC),
                completed_at=None,
                ended_at=None,
            )
        )
        self._db.commit()
        return DateStartResult(session_id=session.id, event_id=event_code, step=first_step)

    def move(self, *, user_id: str, session_id: str, sequence_no: int, choice_id: str, idempotency_key: str) -> DateMoveResult:
        session = self._get_user_session(user_id=user_id, session_id=session_id)
        existing = self._dates.get_move_by_idempotency_key(session_id=session_id, idempotency_key=idempotency_key)
        if existing is not None:
            event_code = str(session.state_json["event_code"])
            return DateMoveResult(
                session_id=session.id,
                status=session.status,
                step=self._rules.next_step(event_code=event_code, current_sequence_no=existing.sequence_no),
                partial_feedback=existing.rule_result_json,
            )
        if session.status != "active":
            raise ValueError("Date session is not active")
        expected_sequence = int(session.state_json.get("next_sequence_no", 1))
        if sequence_no != expected_sequence:
            raise ValueError("Invalid date step sequence")

        event_code = str(session.state_json["event_code"])
        score_delta = self._rules.score_choice(event_code=event_code, sequence_no=sequence_no, choice_id=choice_id)
        total_score = int(session.state_json.get("score", 0)) + score_delta
        next_step = self._rules.next_step(event_code=event_code, current_sequence_no=sequence_no)
        session.state_json = {"event_code": event_code, "score": total_score, "next_sequence_no": sequence_no + 1}
        move = self._dates.add_move(
            GameMove(
                id=str(uuid4()),
                session_id=session.id,
                sequence_no=sequence_no,
                actor="user",
                move_type="choice",
                payload_json={"choice_id": choice_id},
                rule_result_json={"score_delta": score_delta, "score": total_score},
                idempotency_key=idempotency_key,
                created_at=datetime.now(UTC),
            )
        )
        self._db.commit()
        return DateMoveResult(
            session_id=session.id,
            status=session.status,
            step=next_step,
            partial_feedback=move.rule_result_json,
        )

    def finish(self, *, user_id: str, session_id: str) -> DateFinishResult:
        session = self._get_user_session(user_id=user_id, session_id=session_id)
        if session.status == "completed":
            return self._finished_result(session)
        if session.status != "active":
            raise ValueError("Date session is not active")

        event_code = str(session.state_json["event_code"])
        score = int(session.state_json.get("score", 0))
        rule_result = self._rules.finish(event_code=event_code, score=score)
        relationship = self._relationship.apply_chat_event(
            user_id=user_id,
            character_id=session.character_id,
            source_message_id=session.id,
            event_type=f"{event_code}_{rule_result.result}",
            delta=rule_result.relationship_delta,
        )
        reward = self._get_or_create_reward(
            session=session,
            reward_type=rule_result.reward_type,
            reward_status=rule_result.reward_status,
        )
        session.status = "completed"
        session.result = rule_result.result
        session.score = rule_result.score
        session.relationship_event_id = relationship.event_id
        session.reward_event_id = reward.id
        session.completed_at = datetime.now(UTC)
        self._db.commit()
        return DateFinishResult(
            session_id=session.id,
            result=rule_result.result,
            score=rule_result.score,
            airi_reaction=rule_result.airi_reaction,
            relationship_event_id=relationship.event_id,
            relationship_summary=relationship.summary,
            reward_event_id=reward.id,
            reward_status=reward.status,
            reward_type=reward.reward_type,
        )

    def ensure_default_templates(self) -> None:
        for event_code, title, minutes, reward_policy in DEFAULT_DATE_EVENTS:
            if self._dates.get_template_by_code(event_code) is None:
                self._dates.add_template(
                    DateEventTemplate(
                        id=str(uuid4()),
                        event_code=event_code,
                        version=1,
                        title=title,
                        required_relationship_level=1,
                        entry_cost=0,
                        estimated_minutes=minutes,
                        reward_policy_json=reward_policy,
                        status="public",
                        enabled=1,
                        created_at=datetime.now(UTC),
                    )
                )
        self._db.flush()

    def _get_user_session(self, *, user_id: str, session_id: str) -> DateGameSession:
        session = self._dates.get_session(session_id)
        if session is None or session.user_id != user_id:
            raise ValueError("Date session was not found")
        return session

    def _get_template_by_id(self, template_id: str) -> DateEventTemplate:
        for template in self._dates.list_public_templates():
            if template.id == template_id:
                return template
        raise ValueError("Date event template was not found")

    def _get_or_create_reward(self, *, session: DateGameSession, reward_type: str, reward_status: str) -> RewardEvent:
        existing = self._dates.get_reward_for_source(
            user_id=session.user_id,
            source_type="date_event",
            source_id=session.id,
            reward_type=reward_type,
        )
        if existing is not None:
            return existing
        return self._dates.add_reward(
            RewardEvent(
                id=str(uuid4()),
                user_id=session.user_id,
                character_id=session.character_id,
                source_type="date_event",
                source_id=session.id,
                reward_type=reward_type,
                reward_ref=None,
                status=reward_status,
                rule_version=RULE_VERSION,
                idempotency_key=f"date-finish:{session.id}:{reward_type}",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

    def _finished_result(self, session: DateGameSession) -> DateFinishResult:
        reward = self._dates.get_reward_for_source(
            user_id=session.user_id,
            source_type="date_event",
            source_id=session.id,
            reward_type="image",
        ) or self._dates.get_reward_for_source(
            user_id=session.user_id,
            source_type="date_event",
            source_id=session.id,
            reward_type="note",
        ) or self._dates.get_reward_for_source(
            user_id=session.user_id,
            source_type="date_event",
            source_id=session.id,
            reward_type="voice",
        )
        return DateFinishResult(
            session_id=session.id,
            result=session.result or "neutral",
            score=session.score or 0,
            airi_reaction="I already saved the result of this date.",
            relationship_event_id=session.relationship_event_id,
            relationship_summary=None,
            reward_event_id=reward.id if reward is not None else session.reward_event_id,
            reward_status=reward.status if reward is not None else None,
            reward_type=reward.reward_type if reward is not None else None,
        )
