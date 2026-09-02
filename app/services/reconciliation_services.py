import time
from datetime import datetime, timezone

from opentelemetry.trace import Status, StatusCode
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    MatchResultLedgerORM,
    MatchResultORM,
    ReconciliationRun,
    SettlementORM,
)
from app.domain.enums import MatchStatus
from app.domain.models import SettlementRecord
from app.domain.reconciliation.hybrid_resolver import HybridResolver
from app.domain.reconciliation.policy import PolicyAction
from app.domain.reconciliation.state import ReconciliationState
from app.observability.logging import (
    bind_run_id,
    bind_settlement_id,
    clear_observability_context,
    clear_settlement_id,
    log_reconciliation_decision,
    log_reconciliation_failure,
)
from app.observability.metrics import (
    reconciliation_duration_seconds,
    reconciliation_exceptions_total,
    reconciliation_matches_total,
    reconciliation_records_total,
)
from app.observability.tracing import get_tracer
from app.repositories.run_repository import RunRepository


tracer = get_tracer()


class ReconciliationService:
    """
    Orchestrates reconciliation runs and isolates failures
    at the settlement-record level.

    Responsibilities:
        - create or reuse a reconciliation run
        - process settlements independently
        - persist match results
        - isolate record failures
        - maintain explicit run state
        - emit record-level observability signals
        - create application-level tracing spans

    It does NOT:
        - implement reconciliation rules
        - call an LLM directly
        - decide reconciliation policy
        - own LLM-specific metrics
    """

    def __init__(
        self,
        session: AsyncSession,
        resolver: HybridResolver,
    ) -> None:
        self.session = session
        self.resolver = resolver
        self.run_repository = RunRepository(session)

    async def process_run(
        self,
        *,
        idempotency_key: str,
        settlements: list[SettlementORM],
    ) -> ReconciliationRun:
        """
        Process all settlements belonging to one reconciliation run.

        The run context is bound for the lifetime of the run.
        Each settlement gets its own settlement-scoped context.

        Record failures are isolated so that one failed settlement
        does not abort processing of the remaining records.
        """

        run = await self.run_repository.get_or_create(
            idempotency_key=idempotency_key,
        )

        run_id = run.id

        # Convert ORM objects to domain objects before record-level
        # transaction processing begins.
        records = [
            (
                settlement.settlement_id,
                self._to_domain_settlement(
                    settlement
                ),
            )
            for settlement in settlements
        ]

        run.status = ReconciliationState.PROCESSING.value

        await self.session.commit()

        # ---------------------------------------------------------
        # Bind run-level correlation context.
        # ---------------------------------------------------------

        bind_run_id(run_id)

        try:
            for settlement_id, settlement in records:
                await self._process_record(
                    run_id=run_id,
                    settlement_id=settlement_id,
                    settlement=settlement,
                )

        finally:
            # Remove all run-scoped observability context after
            # the run has finished.
            clear_observability_context()

        # Record-level commits can expire the original ORM run
        # instance, so retrieve a fresh instance.
        run = await self.run_repository.get_by_idempotency_key(
            idempotency_key,
        )

        if run is None:
            raise RuntimeError(
                "Reconciliation run disappeared during processing"
            )

        run.status = ReconciliationState.COMPLETED.value
        run.completed_at = datetime.now(
            timezone.utc
        )

        await self.session.commit()

        return run

    async def _process_record(
        self,
        *,
        run_id: int,
        settlement_id: str,
        settlement: SettlementRecord,
    ) -> None:
        """
        Process exactly one settlement.

        Each record receives:
            - settlement-level logging context
            - one application-level tracing span
            - record-level metrics

        A failure in one record is isolated from the remaining
        records in the reconciliation run.

        Observability failures must never change the business
        outcome of a successfully reconciled record.
        """

        reconciliation_records_total.inc()

        bind_settlement_id(settlement_id)

        start = time.perf_counter()

        # ---------------------------------------------------------
        # Parent span for the complete record lifecycle.
        #
        # Nested spans created by lower-level components can
        # automatically become children of this span.
        # ---------------------------------------------------------

        with tracer.start_as_current_span(
            "reconciliation.record"
        ) as span:

            span.set_attribute(
                "run_id",
                run_id,
            )

            span.set_attribute(
                "settlement_id",
                settlement_id,
            )

            try:
                # -------------------------------------------------
                # 1. Resolve the settlement.
                # -------------------------------------------------

                resolution = await self.resolver.resolve(
                    settlement
                )

                # -------------------------------------------------
                # Trace high-value outcome metadata.
                # -------------------------------------------------

                span.set_attribute(
                    "decision",
                    resolution.action.value,
                )

                span.set_attribute(
                    "candidate_count",
                    len(
                        resolution.candidate_ids
                    ),
                )

                span.set_attribute(
                    "llm_invoked",
                    resolution.llm_invoked,
                )

                # -------------------------------------------------
                # 2. Translate policy action into persistence status.
                # -------------------------------------------------

                status = self._map_action_to_status(
                    resolution.action
                )

                # -------------------------------------------------
                # 3. Persist reconciliation result.
                # -------------------------------------------------

                match_result = MatchResultORM(
                    run_id=run_id,
                    settlement_id=settlement_id,
                    status=status,
                    confidence=resolution.confidence,
                    source="hybrid_resolver",
                    evidence={
                        "codes": list(
                            resolution.evidence_codes
                        ),
                        "reason": resolution.reason,
                        "llm_invoked": (
                            resolution.llm_invoked
                        ),
                    },
                    created_at=datetime.now(
                        timezone.utc
                    ),
                )

                self.session.add(match_result)

                await self.session.flush()

                # Persist all selected ledger relationships.
                for ledger_id in resolution.candidate_ids:
                    self.session.add(
                        MatchResultLedgerORM(
                            match_result=match_result,
                            ledger_id=ledger_id,
                        )
                    )

                await self.session.commit()

                # -------------------------------------------------
                # 4. Record business outcome metrics.
                # -------------------------------------------------

                if (
                    resolution.action
                    == PolicyAction.AUTO_MATCH
                ):
                    reconciliation_matches_total.inc()
                else:
                    reconciliation_exceptions_total.inc()

                duration_ms = (
                    time.perf_counter() - start
                ) * 1000

                # -------------------------------------------------
                # 5. Emit final decision event.
                # -------------------------------------------------

                try:
                    log_reconciliation_decision(
                        decision=resolution.action.value,
                        source="hybrid_resolver",
                        confidence=resolution.confidence,
                        selected_candidate_count=len(
                            resolution.candidate_ids
                        ),
                        llm_invoked=(
                            resolution.llm_invoked
                        ),
                        duration_ms=duration_ms,
                    )

                except Exception:
                    # Logging must never turn a successful business
                    # operation into a failed reconciliation.
                    pass

            except Exception as exc:
                # -------------------------------------------------
                # Mark tracing span as failed.
                # -------------------------------------------------

                span.record_exception(exc)

                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                duration_ms = (
                    time.perf_counter() - start
                ) * 1000

                # -------------------------------------------------
                # 6. Record failure metrics.
                # -------------------------------------------------

                reconciliation_exceptions_total.inc()

                # -------------------------------------------------
                # 7. Emit failure event.
                # -------------------------------------------------

                try:
                    log_reconciliation_failure(
                        error_type=type(exc).__name__,
                        duration_ms=duration_ms,
                    )

                except Exception:
                    # Observability is deliberately best-effort.
                    pass

                # -------------------------------------------------
                # 8. Roll back failed transaction.
                # -------------------------------------------------

                await self.session.rollback()

                # -------------------------------------------------
                # 9. Persist isolated FAILED result.
                # -------------------------------------------------

                await self._mark_record_failed(
                    run_id=run_id,
                    settlement_id=settlement_id,
                )

            finally:
                # -------------------------------------------------
                # 10. Always record reconciliation latency.
                # -------------------------------------------------

                reconciliation_duration_seconds.observe(
                    time.perf_counter() - start
                )

                # -------------------------------------------------
                # 11. Remove settlement-specific context.
                #
                # Critical for preventing S001 context from leaking
                # into S002.
                # -------------------------------------------------

                clear_settlement_id()

    async def _mark_record_failed(
        self,
        *,
        run_id: int,
        settlement_id: str,
    ) -> None:
        """
        Persist a FAILED result after the failed record transaction
        has been rolled back.
        """

        failed_result = MatchResultORM(
            run_id=run_id,
            settlement_id=settlement_id,
            status=MatchStatus.FAILED.value,
            confidence=0.0,
            source="reconciliation_service",
            evidence={
                "codes": [
                    "record_processing_failed",
                ],
            },
            created_at=datetime.now(
                timezone.utc
            ),
        )

        self.session.add(failed_result)

        await self.session.commit()

    @staticmethod
    def _map_action_to_status(
        action: PolicyAction,
    ) -> str:
        """
        Translate a domain policy action into the
        persistence-layer reconciliation status.
        """

        if action == PolicyAction.AUTO_MATCH:
            return MatchStatus.MATCHED_AI.value

        if action == PolicyAction.HUMAN_REVIEW:
            return MatchStatus.HUMAN_REVIEW.value

        if action == PolicyAction.NO_MATCH:
            return MatchStatus.NO_MATCH.value

        raise ValueError(
            f"Unsupported policy action: {action.value}"
        )

    @staticmethod
    def _to_domain_settlement(
        settlement: SettlementORM,
    ) -> SettlementRecord:
        """
        Convert the persistence model into a domain model.

        Domain reconciliation logic should not operate directly
        on ORM objects.
        """

        return SettlementRecord(
            settlement_id=settlement.settlement_id,
            merchant_id=settlement.merchant_id,
            amount=settlement.amount,
            currency=settlement.currency,
            settlement_date=settlement.settlement_date,
            reference=settlement.reference,
        )