from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.db.models import LedgerORM
from app.db.session import SessionFactory
from app.domain.enums import LedgerEntryType
from app.repositories.ledger_repository import LedgerRepository


@pytest.mark.asyncio
async def test_create_and_get_ledger():
    async with SessionFactory() as session:
        repository = LedgerRepository(session)

        ledger = LedgerORM(
            ledger_id="TEST-REPO-L001",
            merchant_id="M001",
            amount=Decimal("1500.25"),
            currency="INR",
            transaction_date=date(2026, 8, 25),
            reference="UTR-REPO-001",
            entry_type=LedgerEntryType.PAYMENT.value,
            created_at=datetime.now(timezone.utc),
        )

        created = await repository.create(ledger)

        assert created.ledger_id == "TEST-REPO-L001"

        fetched = await repository.get_by_id(
            "TEST-REPO-L001"
        )

        assert fetched is not None
        assert fetched.ledger_id == "TEST-REPO-L001"
        assert fetched.merchant_id == "M001"
        assert fetched.amount == Decimal("1500.25")
        assert fetched.reference == "UTR-REPO-001"


@pytest.mark.asyncio
async def test_find_candidates_filters_by_merchant_amount_and_date():
    async with SessionFactory() as session:
        repository = LedgerRepository(session)

        candidates = [
            LedgerORM(
                ledger_id="TEST-REPO-C001",
                merchant_id="M900",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="REF-001",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-REPO-C002",
                merchant_id="M900",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 26),
                reference="REF-002",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-REPO-C003",
                merchant_id="M901",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="REF-003",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-REPO-C004",
                merchant_id="M900",
                amount=Decimal("1500.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="REF-004",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
        ]

        for ledger in candidates:
            await repository.create(ledger)

        results = await repository.find_candidates(
            merchant_id="M900",
            amount=Decimal("1000.00"),
            transaction_date=date(2026, 8, 25),
            date_window_days=1,
        )

        result_ids = {
            ledger.ledger_id
            for ledger in results
        }

        assert result_ids == {
            "TEST-REPO-C001",
            "TEST-REPO-C002",
        }

@pytest.mark.asyncio
async def test_find_by_reference_and_amount():
    async with SessionFactory() as session:
        repository = LedgerRepository(session)

        records = [
            LedgerORM(
                ledger_id="TEST-REF-C001",
                merchant_id="M900",
                amount=Decimal("1250.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="UTR-EXACT-001",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-REF-C002",
                merchant_id="M901",
                amount=Decimal("1250.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="UTR-EXACT-001",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-REF-C003",
                merchant_id="M900",
                amount=Decimal("1250.01"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="UTR-EXACT-001",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
        ]

        for record in records:
            await repository.create(record)

        results = await repository.find_by_reference_and_amount(
            reference="UTR-EXACT-001",
            amount=Decimal("1250.00"),
        )

        result_ids = {
            ledger.ledger_id
            for ledger in results
        }

        assert result_ids == {
            "TEST-REF-C001",
            "TEST-REF-C002",
        }