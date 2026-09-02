import time
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LedgerORM
from app.observability.logging import (
    log_candidate_retrieval,
)
from app.observability.metrics import (
    candidate_retrieval_candidates,
    candidate_retrieval_duration_seconds,
    candidate_retrieval_empty_total,
    candidate_retrieval_total,
)


class CandidateRetriever:
    """
    Database-backed candidate retrieval for reconciliation.

    Responsibilities:
        - retrieve a bounded candidate set
        - apply retrieval-level filtering
        - provide retrieval telemetry

    It does NOT:
        - decide the final reconciliation outcome
        - calculate reconciliation confidence
        - apply business matching rules
        - invoke the LLM
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
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
        """
        Return a bounded set of plausible ledger candidates.

        Retrieval telemetry is emitted after a successful retrieval.
        Retrieval latency is always recorded, including failures.
        """

        candidate_retrieval_total.inc()

        start = time.perf_counter()

        # Keep an explicit default so observability remains safe even
        # if the database query raises before candidates are assigned.
        candidates: list[LedgerORM] = []

        try:
            start_date = (
                transaction_date
                - timedelta(days=date_window_days)
            )

            end_date = (
                transaction_date
                + timedelta(days=date_window_days)
            )

            min_amount = (
                amount - amount_tolerance
            )

            max_amount = (
                amount + amount_tolerance
            )

            # -----------------------------------------------------
            # Primary retrieval
            #
            # Strong deterministic retrieval signals:
            #   merchant + currency + amount + date
            # -----------------------------------------------------

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

            # -----------------------------------------------------
            # Reference-aware preference
            #
            # When primary retrieval succeeds and a reference is
            # available, prefer exact-reference candidates.
            #
            # We keep the original candidate set if no exact
            # reference candidate exists.
            # -----------------------------------------------------

            if candidates and reference is not None:
                exact_reference_candidates = [
                    ledger
                    for ledger in candidates
                    if ledger.reference == reference
                ]

                if exact_reference_candidates:
                    candidates = (
                        exact_reference_candidates
                    )

            # -----------------------------------------------------
            # Reference-aware fallback
            #
            # Used when the primary amount/date retrieval returns
            # nothing but a reference is available.
            # -----------------------------------------------------

            elif not candidates and reference is not None:
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

            # -----------------------------------------------------
            # Retrieval outcome metrics
            # -----------------------------------------------------

            candidate_count = len(candidates)

            candidate_retrieval_candidates.observe(
                candidate_count
            )

            if candidate_count == 0:
                candidate_retrieval_empty_total.inc()

            return candidates

        finally:
            # -----------------------------------------------------
            # Retrieval latency
            #
            # This must execute even if the database operation
            # raises an exception.
            # -----------------------------------------------------

            duration_seconds = (
                time.perf_counter() - start
            )

            candidate_retrieval_duration_seconds.observe(
                duration_seconds
            )

            # -----------------------------------------------------
            # Structured retrieval event
            #
            # Logging is best-effort and must never affect
            # reconciliation behavior.
            # -----------------------------------------------------

            try:
                log_candidate_retrieval(
                    candidate_count=len(candidates),
                    duration_ms=duration_seconds * 1000,
                )
            except Exception:
                pass

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
        """
        Print the SQL generated for the primary retrieval query.

        Intended for development/debugging rather than reconciliation
        execution.
        """

        start_date = (
            transaction_date
            - timedelta(days=date_window_days)
        )

        end_date = (
            transaction_date
            + timedelta(days=date_window_days)
        )

        min_amount = (
            amount - amount_tolerance
        )

        max_amount = (
            amount + amount_tolerance
        )

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