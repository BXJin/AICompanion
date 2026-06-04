from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.domain import CreditBalanceSnapshot, CreditLedger
from app.repositories.credit_ledger import CreditLedgerRepository


@dataclass(frozen=True)
class CreditLedgerResult:
    ledger_id: str
    bucket: str
    delta: int
    balance_after: int
    replayed: bool = False


class InsufficientCreditError(ValueError):
    pass


class CreditLedgerService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._ledger = CreditLedgerRepository(db)

    def grant(
        self,
        *,
        user_id: str,
        bucket: str,
        amount: int,
        reason: str,
        source_type: str,
        source_id: str | None,
        idempotency_key: str,
    ) -> CreditLedgerResult:
        if amount <= 0:
            raise ValueError("Credit grant amount must be positive")
        return self._append(
            user_id=user_id,
            bucket=bucket,
            delta=amount,
            reason=reason,
            source_type=source_type,
            source_id=source_id,
            idempotency_key=idempotency_key,
        )

    def spend(
        self,
        *,
        user_id: str,
        bucket: str,
        amount: int,
        reason: str,
        source_type: str,
        source_id: str | None,
        idempotency_key: str,
    ) -> CreditLedgerResult:
        if amount <= 0:
            raise ValueError("Credit spend amount must be positive")
        snapshot = self._get_or_create_snapshot(user_id=user_id, bucket=bucket)
        if snapshot.balance < amount:
            raise InsufficientCreditError("Insufficient credit balance")
        return self._append(
            user_id=user_id,
            bucket=bucket,
            delta=-amount,
            reason=reason,
            source_type=source_type,
            source_id=source_id,
            idempotency_key=idempotency_key,
        )

    def refund(
        self,
        *,
        user_id: str,
        bucket: str,
        amount: int,
        reason: str,
        source_type: str,
        source_id: str | None,
        idempotency_key: str,
    ) -> CreditLedgerResult:
        return self.grant(
            user_id=user_id,
            bucket=bucket,
            amount=amount,
            reason=reason,
            source_type=source_type,
            source_id=source_id,
            idempotency_key=idempotency_key,
        )

    def replay_balance(self, *, user_id: str, bucket: str) -> int:
        return self._ledger.replay_bucket_balance(user_id=user_id, bucket=bucket)

    def _append(
        self,
        *,
        user_id: str,
        bucket: str,
        delta: int,
        reason: str,
        source_type: str,
        source_id: str | None,
        idempotency_key: str,
    ) -> CreditLedgerResult:
        existing = self._ledger.get_by_idempotency_key(user_id=user_id, idempotency_key=idempotency_key)
        if existing is not None:
            return CreditLedgerResult(
                ledger_id=existing.id,
                bucket=existing.bucket,
                delta=existing.delta,
                balance_after=existing.balance_after or 0,
                replayed=True,
            )

        snapshot = self._get_or_create_snapshot(user_id=user_id, bucket=bucket)
        snapshot.balance += delta
        snapshot.ledger_version += 1
        snapshot.updated_at = datetime.now(UTC)
        row = self._ledger.add_ledger_row(
            CreditLedger(
                id=str(uuid4()),
                user_id=user_id,
                bucket=bucket,
                reason=reason,
                delta=delta,
                source_type=source_type,
                source_id=source_id,
                idempotency_key=idempotency_key,
                balance_after=snapshot.balance,
                created_at=datetime.now(UTC),
                expires_at=None,
            )
        )
        self._db.flush()
        return CreditLedgerResult(
            ledger_id=row.id,
            bucket=bucket,
            delta=delta,
            balance_after=snapshot.balance,
        )

    def _get_or_create_snapshot(self, *, user_id: str, bucket: str) -> CreditBalanceSnapshot:
        snapshot = self._ledger.get_snapshot(user_id=user_id, bucket=bucket)
        if snapshot is not None:
            return snapshot
        return self._ledger.add_snapshot(
            CreditBalanceSnapshot(
                user_id=user_id,
                bucket=bucket,
                balance=0,
                ledger_version=0,
                updated_at=datetime.now(UTC),
            )
        )
