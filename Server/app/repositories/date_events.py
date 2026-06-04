from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import DateEventTemplate, DateGameSession, GameMove, RewardEvent


class DateEventRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add_template(self, template: DateEventTemplate) -> DateEventTemplate:
        self._db.add(template)
        return template

    def list_public_templates(self) -> list[DateEventTemplate]:
        statement = (
            select(DateEventTemplate)
            .where(DateEventTemplate.enabled == 1, DateEventTemplate.status == "public")
            .order_by(DateEventTemplate.event_code.asc(), DateEventTemplate.version.desc())
        )
        return list(self._db.execute(statement).scalars())

    def get_template_by_code(self, event_code: str) -> DateEventTemplate | None:
        statement = (
            select(DateEventTemplate)
            .where(DateEventTemplate.event_code == event_code, DateEventTemplate.enabled == 1, DateEventTemplate.status == "public")
            .order_by(DateEventTemplate.version.desc())
            .limit(1)
        )
        return self._db.execute(statement).scalar_one_or_none()

    def add_session(self, session: DateGameSession) -> DateGameSession:
        self._db.add(session)
        return session

    def get_session(self, session_id: str) -> DateGameSession | None:
        return self._db.get(DateGameSession, session_id)

    def get_session_by_idempotency_key(self, *, user_id: str, idempotency_key: str) -> DateGameSession | None:
        statement = select(DateGameSession).where(
            DateGameSession.user_id == user_id,
            DateGameSession.idempotency_key == idempotency_key,
        )
        return self._db.execute(statement).scalar_one_or_none()

    def add_move(self, move: GameMove) -> GameMove:
        self._db.add(move)
        return move

    def get_move_by_idempotency_key(self, *, session_id: str, idempotency_key: str) -> GameMove | None:
        statement = select(GameMove).where(GameMove.session_id == session_id, GameMove.idempotency_key == idempotency_key)
        return self._db.execute(statement).scalar_one_or_none()

    def list_moves(self, *, session_id: str) -> list[GameMove]:
        statement = select(GameMove).where(GameMove.session_id == session_id).order_by(GameMove.sequence_no.asc())
        return list(self._db.execute(statement).scalars())

    def add_reward(self, reward: RewardEvent) -> RewardEvent:
        self._db.add(reward)
        return reward

    def get_reward_for_source(
        self,
        *,
        user_id: str,
        source_type: str,
        source_id: str,
        reward_type: str,
    ) -> RewardEvent | None:
        statement = select(RewardEvent).where(
            RewardEvent.user_id == user_id,
            RewardEvent.source_type == source_type,
            RewardEvent.source_id == source_id,
            RewardEvent.reward_type == reward_type,
        )
        return self._db.execute(statement).scalar_one_or_none()
