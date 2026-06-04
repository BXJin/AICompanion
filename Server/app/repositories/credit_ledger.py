from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.domain import CreditBalanceSnapshot, CreditLedger


class CreditLedgerRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add_ledger_row(self, row: CreditLedger) -> CreditLedger:
        self._db.add(row)
        return row

    def get_by_idempotency_key(self, *, user_id: str, idempotency_key: str) -> CreditLedger | None:
        statement = select(CreditLedger).where(
            CreditLedger.user_id == user_id,
            CreditLedger.idempotency_key == idempotency_key,
        )
        return self._db.execute(statement).scalar_one_or_none()

    def get_snapshot(self, *, user_id: str, bucket: str) -> CreditBalanceSnapshot | None:
        return self._db.get(CreditBalanceSnapshot, {"user_id": user_id, "bucket": bucket})

    def add_snapshot(self, snapshot: CreditBalanceSnapshot) -> CreditBalanceSnapshot:
        self._db.add(snapshot)
        return snapshot

    def replay_bucket_balance(self, *, user_id: str, bucket: str) -> int:
        statement = select(func.coalesce(func.sum(CreditLedger.delta), 0)).where(
            CreditLedger.user_id == user_id,
            CreditLedger.bucket == bucket,
        )
        return int(self._db.execute(statement).scalar_one())
