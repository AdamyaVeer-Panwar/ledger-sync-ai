from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.db.models import LedgerORM
from app.db.session import SessionFactory
from app.domain.enums import LedgerEntryType
from app.repositories.candidate_retriever import CandidateRetriever


@pytest.mark.asyncio
async def test_retrieve_candidates_uses_filters():
    async with SessionFactory() as session:
        retriever = CandidateRetriever(session)

        records = [
            LedgerORM(
                ledger_id="TEST-RETRIEVER-001",
                merchant_id="M800",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="REF-001",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-RETRIEVER-002",
                merchant_id="M800",
                amount=Decimal("1001.00"),
                currency="INR",
                transaction_date=date(2026, 8, 26),
                reference="REF-002",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
            LedgerORM(
                ledger_id="TEST-RETRIEVER-003",
                merchant_id="M801",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="REF-003",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            ),
        ]

        session.add_all(records)
        await session.flush()

        candidates = await retriever.retrieve(
            merchant_id="M800",
            currency="INR",
            amount=Decimal("1000.00"),
            transaction_date=date(2026, 8, 25),
            amount_tolerance=Decimal("0.02"),
            date_window_days=2,
        )

        result_ids = {
            ledger.ledger_id
            for ledger in candidates
        }

        assert result_ids == {
            "TEST-RETRIEVER-001",
        }