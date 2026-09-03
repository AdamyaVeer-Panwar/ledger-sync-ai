from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.db.models import LedgerORM, ReconciliationRun, SettlementORM
from app.db.session import SessionFactory
from app.domain.enums import LedgerEntryType
from sqlalchemy.exc import IntegrityError
from app.db.models import MatchResultORM

from sqlalchemy import insert

@pytest.mark.asyncio
async def test_insert_settlement_record():
    async with SessionFactory() as session:
        run = ReconciliationRun(
            idempotency_key="TEST-RUN-DB-INSERT",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        settlement = SettlementORM(
            settlement_id="TEST-S001-insert",
            run=run,
            merchant_id="M001",
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-TEST-S001",
            created_at=datetime.now(timezone.utc),
        )

        session.add(settlement)

        await session.flush()

        assert settlement.settlement_id == "TEST-S001-insert"
        assert settlement.amount == Decimal("1000.00")


@pytest.mark.asyncio
async def test_insert_ledger_record():
    async with SessionFactory() as session:
        ledger = LedgerORM(
            ledger_id="TEST-L001-insert",
            merchant_id="M001",
            amount=Decimal("1000.00"),
            currency="INR",
            transaction_date=date(2026, 8, 25),
            reference="UTR-TEST-L001",
            entry_type=LedgerEntryType.PAYMENT.value,
            created_at=datetime.now(timezone.utc),
        )

        session.add(ledger)

        await session.flush()

        assert ledger.ledger_id == "TEST-L001-insert"
        assert ledger.amount == Decimal("1000.00")
        assert ledger.entry_type == LedgerEntryType.PAYMENT.value


@pytest.mark.asyncio
async def test_settlement_requires_valid_run():
    async with SessionFactory() as session:
        settlement = SettlementORM(
            settlement_id="TEST-S-FK",
            run_id=999999,
            merchant_id="M001",
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-TEST-FK",
            created_at=datetime.now(timezone.utc),
        )

        session.add(settlement)

        with pytest.raises(IntegrityError):
            await session.flush()

        await session.rollback()



@pytest.mark.asyncio
async def test_settlement_id_must_be_unique():
    async with SessionFactory() as session:
        run = ReconciliationRun(
            idempotency_key="TEST-RUN-DB-UNIQUE",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        first = SettlementORM(
            settlement_id="TEST-S-UNIQUE",
            run=run,
            merchant_id="M001",
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-UNIQUE-1",
            created_at=datetime.now(timezone.utc),
        )

        session.add(first)
        await session.flush()

        duplicate = insert(SettlementORM).values(
            settlement_id="TEST-S-UNIQUE",
            run_id=run.id,
            merchant_id="M002",
            amount=Decimal("500.00"),
            currency="INR",
            settlement_date=date(2026, 8, 26),
            reference="UTR-UNIQUE-2",
            created_at=datetime.now(timezone.utc),
        )

        with pytest.raises(IntegrityError):
            await session.execute(duplicate)

        await session.rollback()

@pytest.mark.asyncio
async def test_settlement_amount_must_be_positive():
    async with SessionFactory() as session:
        run = ReconciliationRun(
            idempotency_key="TEST-RUN-DB-INSERT",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        settlement = SettlementORM(
            settlement_id="TEST-S-CHECK",
            run=run,
            merchant_id="M001",
            amount=Decimal("-1.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-CHECK",
            created_at=datetime.now(timezone.utc),
        )

        session.add(settlement)

        with pytest.raises(IntegrityError):
            await session.flush()

        await session.rollback()


@pytest.mark.asyncio
async def test_match_confidence_must_be_between_zero_and_one():
    async with SessionFactory() as session:
        run = ReconciliationRun(
            idempotency_key="TEST-RUN-DB-INSERT",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        settlement = SettlementORM(
            settlement_id="TEST-S-CONFIDENCE",
            run=run,
            merchant_id="M001",
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-CONFIDENCE",
            created_at=datetime.now(timezone.utc),
        )

        await session.flush()

        result = MatchResultORM(
            run=run,
            settlement=settlement,
            status="MATCHED_RULE",
            confidence=Decimal("1.50"),
            source="RULES",
            evidence={},
            created_at=datetime.now(timezone.utc),
        )

        session.add(result)

        with pytest.raises(IntegrityError):
            await session.flush()

        await session.rollback()


@pytest.mark.asyncio
async def test_money_uses_decimal_precision():
    async with SessionFactory() as session:
        run = ReconciliationRun(
            idempotency_key="TEST-RUN-DB-INSERT",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        settlement = SettlementORM(
            settlement_id="TEST-S-DECIMAL",
            run=run,
            merchant_id="M001",
            amount=Decimal("1234567890123456.78"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-DECIMAL",
            created_at=datetime.now(timezone.utc),
        )

        session.add(settlement)
        await session.flush()

        assert settlement.amount == Decimal("1234567890123456.78")
        assert isinstance(settlement.amount, Decimal)

        await session.rollback()