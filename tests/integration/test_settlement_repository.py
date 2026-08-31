from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.db.models import ReconciliationRun, SettlementORM
from app.db.session import SessionFactory
from app.repositories.settlement_repository import SettlementRepository


@pytest.mark.asyncio
async def test_create_and_get_settlement():
    async with SessionFactory() as session:
        repository = SettlementRepository(session)

        run = ReconciliationRun(
            idempotency_key="TEST-SETTLEMENT-REPOSITORY-001",
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        settlement = SettlementORM(
            settlement_id="TEST-REPO-S001",
            run=run,
            merchant_id="M900",
            amount=Decimal("1250.00"),
            currency="INR",
            settlement_date=date(2026, 8, 25),
            reference="UTR-REPO-S001",
            created_at=datetime.now(timezone.utc),
        )

        created = await repository.create(settlement)

        assert created.settlement_id == "TEST-REPO-S001"

        fetched = await repository.get_by_id(
            "TEST-REPO-S001"
        )

        assert fetched is not None
        assert fetched.merchant_id == "M900"
        assert fetched.amount == Decimal("1250.00")
        assert fetched.reference == "UTR-REPO-S001"