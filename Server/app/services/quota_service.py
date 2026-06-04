from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import PlanAllowance, QuotaCounter
from app.repositories.quotas import QuotaRepository


DEFAULT_ALLOWANCES = {
    ("free", "text_turn", "daily"): 50,
    ("free", "voice_second", "daily"): 60,
    ("free", "tts_reply", "daily"): 5,
    ("free", "image_reward", "daily"): 1,
    ("free", "date_event", "daily"): 3,
}


@dataclass(frozen=True)
class QuotaCheckResult:
    allowed: bool
    remaining: int
    limit: int
    used: int


class QuotaExceededError(ValueError):
    pass


class QuotaService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._quotas = QuotaRepository(db)

    def ensure_default_allowances(self) -> None:
        for (plan, feature, period_type), limit_amount in DEFAULT_ALLOWANCES.items():
            existing = self._quotas.get_allowance(plan=plan, feature=feature, period_type=period_type)
            if existing is None:
                self._quotas.add_allowance(
                    PlanAllowance(
                        id=str(uuid4()),
                        plan=plan,
                        feature=feature,
                        period_type=period_type,
                        limit_amount=limit_amount,
                        version=1,
                        enabled=1,
                        created_at=datetime.now(UTC),
                    )
                )
        self._db.flush()

    def remaining(self, *, user_id: str, plan: str, feature: str, amount: int = 1) -> QuotaCheckResult:
        allowance = self._get_allowance(plan=plan, feature=feature)
        counter = self._get_or_create_counter(user_id=user_id, plan=plan, feature=feature, allowance=allowance)
        remaining = max(0, counter.limit_amount - counter.used_amount)
        return QuotaCheckResult(
            allowed=remaining >= amount,
            remaining=remaining,
            limit=counter.limit_amount,
            used=counter.used_amount,
        )

    def consume(self, *, user_id: str, plan: str, feature: str, amount: int = 1) -> QuotaCheckResult:
        if amount <= 0:
            raise ValueError("Quota amount must be positive")
        allowance = self._get_allowance(plan=plan, feature=feature)
        counter = self._get_or_create_counter(user_id=user_id, plan=plan, feature=feature, allowance=allowance)
        if counter.used_amount + amount > counter.limit_amount:
            remaining = max(0, counter.limit_amount - counter.used_amount)
            raise QuotaExceededError(f"{feature} quota exceeded: {remaining} remaining")
        counter.used_amount += amount
        counter.updated_at = datetime.now(UTC)
        self._db.flush()
        return QuotaCheckResult(
            allowed=True,
            remaining=max(0, counter.limit_amount - counter.used_amount),
            limit=counter.limit_amount,
            used=counter.used_amount,
        )

    def _get_allowance(self, *, plan: str, feature: str) -> PlanAllowance:
        self.ensure_default_allowances()
        allowance = self._quotas.get_allowance(plan=plan, feature=feature, period_type="daily")
        if allowance is None:
            raise ValueError(f"Missing quota allowance for {plan}:{feature}")
        return allowance

    def _get_or_create_counter(
        self,
        *,
        user_id: str,
        plan: str,
        feature: str,
        allowance: PlanAllowance,
    ) -> QuotaCounter:
        today = date.today()
        counter = self._quotas.get_counter(
            user_id=user_id,
            feature=feature,
            period_type=allowance.period_type,
            period_start=today,
        )
        if counter is not None:
            return counter
        return self._quotas.add_counter(
            QuotaCounter(
                id=str(uuid4()),
                user_id=user_id,
                plan=plan,
                feature=feature,
                period_type=allowance.period_type,
                period_start=today,
                used_amount=0,
                limit_amount=allowance.limit_amount,
                updated_at=datetime.now(UTC),
            )
        )
