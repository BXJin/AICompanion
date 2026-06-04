from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import PlanAllowance, QuotaCounter


class QuotaRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add_allowance(self, allowance: PlanAllowance) -> PlanAllowance:
        self._db.add(allowance)
        return allowance

    def get_allowance(self, *, plan: str, feature: str, period_type: str = "daily") -> PlanAllowance | None:
        statement = (
            select(PlanAllowance)
            .where(
                PlanAllowance.plan == plan,
                PlanAllowance.feature == feature,
                PlanAllowance.period_type == period_type,
                PlanAllowance.enabled == 1,
            )
            .order_by(PlanAllowance.version.desc())
            .limit(1)
        )
        return self._db.execute(statement).scalar_one_or_none()

    def add_counter(self, counter: QuotaCounter) -> QuotaCounter:
        self._db.add(counter)
        return counter

    def get_counter(
        self,
        *,
        user_id: str,
        feature: str,
        period_type: str,
        period_start,
    ) -> QuotaCounter | None:
        statement = select(QuotaCounter).where(
            QuotaCounter.user_id == user_id,
            QuotaCounter.feature == feature,
            QuotaCounter.period_type == period_type,
            QuotaCounter.period_start == period_start,
        )
        return self._db.execute(statement).scalar_one_or_none()
