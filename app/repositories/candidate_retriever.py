from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LedgerORM


class CandidateRetriever:
    """Database-backed candidate retrieval for reconciliation.

    Responsibility:
        Retrieve a bounded set of plausible ledger candidates.

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

        # ---------------------------------------------------------
        # Primary retrieval
        #
        # Strong deterministic signals:
        #   merchant + currency + amount + date
        # ---------------------------------------------------------

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

        candidates = list(
            result.scalars().all()
        )

        # ---------------------------------------------------------
        # Reference-aware preference
        #
        # If primary retrieval found candidates and an exact
        # reference is present, prefer the exact reference rows.
        #
        # We intentionally keep the old behavior here because
        # exact reference matches are a strong signal.
        # ---------------------------------------------------------

        if candidates and reference is not None:

            exact_reference_candidates = [
                ledger
                for ledger in candidates
                if ledger.reference == reference
            ]

            if exact_reference_candidates:
                return exact_reference_candidates

            return candidates

        # ---------------------------------------------------------
        # Fallback retrieval
        #
        # IMPORTANT:
        #
        # Some reconciliation scenarios intentionally have
        # different individual ledger amounts from the settlement
        # amount.
        #
        # Example:
        #
        #   settlement = 8141.50 - 60.44
        #
        # The primary amount filter cannot retrieve either ledger.
        #
        # In that situation, use merchant + currency + date +
        # reference-family as a broader retrieval strategy.
        # ---------------------------------------------------------

        if not candidates and reference is not None:

            reference_fallback_stmt = (
                select(LedgerORM)
                .where(
                    LedgerORM.merchant_id == merchant_id,
                    LedgerORM.currency == currency,
                    LedgerORM.transaction_date.between(
                        start_date,
                        end_date,
                    ),
                    LedgerORM.reference.like(
                        f"{reference}%"
                    ),
                )
                .order_by(
                    LedgerORM.transaction_date,
                    LedgerORM.ledger_id,
                )
                .limit(limit)
            )

            fallback_result = (
                await self.session.execute(
                    reference_fallback_stmt
                )
            )

            candidates = list(
                fallback_result.scalars().all()
            )

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
            compile_kwargs={
                "literal_binds": True
            },
        )

        print(compiled)