from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LedgerORM


class CandidateRetriever:
    """Database-backed candidate retrieval for reconciliation.

    Responsibility:
        Retrieve a bounded set of plausible ledger records.

    It does NOT:
        - decide the final match
        - calculate confidence
        - apply reconciliation business rules
        - call an LLM
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def retrieve(
        self,
        *,
        merchant_id: str,
        currency: str,
        amount: Decimal,
        transaction_date: date,
        amount_tolerance: Decimal = Decimal("0.02"),
        date_window_days: int = 2,
        reference: str | None = None,
        limit: int = 50,
    ) -> list[LedgerORM]:
        """Return a bounded set of plausible ledger candidates."""

        start_date = transaction_date - timedelta(
            days=date_window_days
        )
        end_date = transaction_date + timedelta(
            days=date_window_days
        )

        min_amount = amount - amount_tolerance
        max_amount = amount + amount_tolerance

        stmt = (
            select(LedgerORM)
            .where(
                LedgerORM.merchant_id == merchant_id,
                LedgerORM.currency == currency,
                LedgerORM.amount.between(
                    min_amount,
                    max_amount,
                ),
                LedgerORM.transaction_date.between(
                    start_date,
                    end_date,
                ),
            )
            .order_by(
                LedgerORM.transaction_date,
                LedgerORM.ledger_id,
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        candidates = list(result.scalars().all())

        if reference is not None:
            exact_reference_candidates = [
                ledger
                for ledger in candidates
                if ledger.reference == reference
            ]

            if exact_reference_candidates:
                return exact_reference_candidates

        return candidates


    async def explain(
    self,
    *,
    merchant_id: str,
    currency: str,
    amount: Decimal,
    transaction_date: date,
    amount_tolerance: Decimal = Decimal("0.02"),
    date_window_days: int = 2,
    ) -> None:
        start_date = transaction_date - timedelta(
        days=date_window_days
        )
        end_date = transaction_date + timedelta(
        days=date_window_days
        )

        min_amount = amount - amount_tolerance
        max_amount = amount + amount_tolerance

        stmt = (
        select(LedgerORM)
        .where(
            LedgerORM.merchant_id == merchant_id,
            LedgerORM.currency == currency,
            LedgerORM.amount.between(
                min_amount,
                max_amount,
            ),
            LedgerORM.transaction_date.between(
                start_date,
                end_date,
            ),
        )
        .order_by(
            LedgerORM.transaction_date,
            LedgerORM.ledger_id,
        )
        .limit(50)
        )

        compiled = stmt.compile(
        self.session.bind.sync_engine,
        compile_kwargs={"literal_binds": True},
        )

        print(compiled)