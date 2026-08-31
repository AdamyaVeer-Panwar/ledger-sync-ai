from datetime import datetime, timezone

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
from app.domain.reconciliation.state import ReconciliationState
from app.repositories.run_repository import RunRepository


class ReconciliationService:
    """
    Orchestrates reconciliation runs and isolates failures
    at the settlement-record level.

    Responsibilities:
        - create/reuse a reconciliation run
        - process settlements independently
        - persist match results
        - isolate record failures
        - maintain explicit run state

    It does NOT:
        - implement reconciliation rules
        - call an LLM directly
        - decide policy
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
        Process all settlements belonging to one run.

        Each settlement is converted to an immutable domain
        representation before any record-level commit occurs.
        """

        run = await self.run_repository.get_or_create(
            idempotency_key=idempotency_key,
        )

        # Capture the run identifier before commit can expire
        # the ORM object's attributes.
        run_id = run.id

        # Convert all ORM settlements before the first record-level
        # transaction boundary. After this point, processing does
        # not depend on ORM settlement objects.
        records = [
            (
                settlement.settlement_id,
                self._to_domain_settlement(settlement),
            )
            for settlement in settlements
        ]

        run.status = ReconciliationState.PROCESSING.value
        await self.session.commit()

        for settlement_id, settlement in records:
            await self._process_record(
                run_id=run_id,
                settlement_id=settlement_id,
                settlement=settlement,
            )

        # The record-level commits may have expired the original
        # run ORM instance, so fetch a fresh one.
        run = await self.run_repository.get_by_idempotency_key(
            idempotency_key,
        )

        if run is None:
            raise RuntimeError(
                "Reconciliation run disappeared during processing"
            )

        run.status = ReconciliationState.COMPLETED.value
        run.completed_at = datetime.now(timezone.utc)

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

        The method receives only:
            - primitive run_id
            - primitive settlement_id
            - plain domain settlement

        This prevents implicit ORM I/O after transaction boundaries.
        """

        try:
            resolution = await self.resolver.resolve(
                settlement
            )

            match_result = MatchResultORM(
                run_id=run_id,
                settlement_id=settlement_id,
                status=self._map_action_to_status(
                    resolution.action
                ),
                confidence=resolution.confidence,
                source="hybrid_resolver",
                evidence={
                    "codes": resolution.evidence_codes,
                    "reason": resolution.reason,
                },
                created_at=datetime.now(timezone.utc),
            )

            self.session.add(match_result)

            await self.session.flush()

            for ledger_id in resolution.candidate_ids:
                self.session.add(
                    MatchResultLedgerORM(
                        match_result=match_result,
                        ledger_id=ledger_id,
                    )
                )

            await self.session.commit()

        except Exception:
            await self.session.rollback()

            await self._mark_record_failed(
                run_id=run_id,
                settlement_id=settlement_id,
            )

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
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(failed_result)

        await self.session.commit()

    @staticmethod
    def _map_action_to_status(
        action,
    ) -> str:
        action_value = action.value

        if action_value == "AUTO_MATCH":
            return MatchStatus.MATCHED_AI.value

        if action_value == "HUMAN_REVIEW":
            return MatchStatus.HUMAN_REVIEW.value

        if action_value == "NO_MATCH":
            return MatchStatus.NO_MATCH.value

        raise ValueError(
            f"Unsupported policy action: {action_value}"
        )

    @staticmethod
    def _to_domain_settlement(
        settlement: SettlementORM,
    ) -> SettlementRecord:
        return SettlementRecord(
            settlement_id=settlement.settlement_id,
            merchant_id=settlement.merchant_id,
            amount=settlement.amount,
            currency=settlement.currency,
            settlement_date=settlement.settlement_date,
            reference=settlement.reference,
        )