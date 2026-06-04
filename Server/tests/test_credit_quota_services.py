import pytest
from sqlalchemy.orm import Session

from app.database import create_session
from app.models.domain import CreditBalanceSnapshot, PlanAllowance, QuotaCounter
from app.models.user import User
from app.services.credit_ledger_service import CreditLedgerService, InsufficientCreditError
from app.services.quota_service import QuotaExceededError, QuotaService


def _create_user(db: Session, user_id: str = "quota-user") -> None:
    db.add(User(id=user_id, auth_provider="guest", is_guest=True, status="active"))
    db.commit()


def test_credit_ledger_grant_spend_refund_and_replay(client, test_settings) -> None:  # type: ignore[no-untyped-def]
    db = create_session(test_settings)
    try:
        _create_user(db)
        service = CreditLedgerService(db)

        grant = service.grant(
            user_id="quota-user",
            bucket="purchased",
            amount=10,
            reason="promo_grant",
            source_type="test",
            source_id="grant-1",
            idempotency_key="grant-1",
        )
        duplicate_grant = service.grant(
            user_id="quota-user",
            bucket="purchased",
            amount=10,
            reason="promo_grant",
            source_type="test",
            source_id="grant-1",
            idempotency_key="grant-1",
        )
        spend = service.spend(
            user_id="quota-user",
            bucket="purchased",
            amount=3,
            reason="media_generation",
            source_type="test",
            source_id="spend-1",
            idempotency_key="spend-1",
        )
        refund = service.refund(
            user_id="quota-user",
            bucket="purchased",
            amount=1,
            reason="provider_refund",
            source_type="test",
            source_id="refund-1",
            idempotency_key="refund-1",
        )
        db.commit()

        snapshot = db.get(CreditBalanceSnapshot, {"user_id": "quota-user", "bucket": "purchased"})
        assert grant.balance_after == 10
        assert duplicate_grant.replayed is True
        assert duplicate_grant.ledger_id == grant.ledger_id
        assert spend.balance_after == 7
        assert refund.balance_after == 8
        assert snapshot is not None
        assert snapshot.balance == 8
        assert service.replay_balance(user_id="quota-user", bucket="purchased") == 8
    finally:
        db.close()


def test_credit_ledger_blocks_overspend(client, test_settings) -> None:  # type: ignore[no-untyped-def]
    db = create_session(test_settings)
    try:
        _create_user(db)

        with pytest.raises(InsufficientCreditError):
            CreditLedgerService(db).spend(
                user_id="quota-user",
                bucket="purchased",
                amount=1,
                reason="media_generation",
                source_type="test",
                source_id="spend-1",
                idempotency_key="spend-1",
            )
    finally:
        db.close()


def test_quota_service_seeds_allowance_and_blocks_after_limit(client, test_settings) -> None:  # type: ignore[no-untyped-def]
    db = create_session(test_settings)
    try:
        _create_user(db)
        service = QuotaService(db)

        first = service.consume(user_id="quota-user", plan="free", feature="text_turn", amount=49)
        second = service.consume(user_id="quota-user", plan="free", feature="text_turn")

        assert first.remaining == 1
        assert second.remaining == 0
        with pytest.raises(QuotaExceededError):
            service.consume(user_id="quota-user", plan="free", feature="text_turn")

        assert db.query(PlanAllowance).filter_by(plan="free", feature="text_turn").count() == 1
        counter = db.query(QuotaCounter).filter_by(user_id="quota-user", feature="text_turn").one()
        assert counter.used_amount == 50
        assert counter.limit_amount == 50
    finally:
        db.close()
