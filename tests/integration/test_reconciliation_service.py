import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

from app.db.models import (
    MatchResultORM,
    ReconciliationRun,
    SettlementORM,
)
from app.db.session import SessionFactory
from app.domain.reconciliation.hybrid_result import (
    HybridResolution,
)
from app.domain.reconciliation.policy import PolicyAction
from app.domain.reconciliation.state import (
    ReconciliationState,
)
from app.infrastructure.llm.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
)
from app.repositories.run_repository import RunRepository
from app.services.reconciliation_services import (
    ReconciliationService,
)


def unique_id(prefix: str) -> str:
    """Return a unique test identifier."""
    return f"{prefix}-{uuid.uuid4().hex}"


class FakeHybridResolver:
    """Resolver that intentionally fails for one settlement."""

    def __init__(
        self,
        failing_settlement_id: str,
    ) -> None:
        self.failing_settlement_id = (
            failing_settlement_id
        )

    async def resolve(self, settlement):
        if (
            settlement.settlement_id
            == self.failing_settlement_id
        ):
            raise RuntimeError(
                "injected resolver failure"
            )

        return HybridResolution(
            settlement_id=settlement.settlement_id,
            action=PolicyAction.AUTO_MATCH,
            candidate_ids=[],
            confidence=0.0,
            evidence_codes=[
                "test_success",
            ],
            reason="test resolution",
        )


def make_settlement(
    settlement_id: str,
    run: ReconciliationRun,
) -> SettlementORM:
    """Create an isolated settlement for integration tests."""

    return SettlementORM(
        settlement_id=settlement_id,
        run=run,
        merchant_id="M001",
        amount=Decimal("1000.00"),
        currency="INR",
        settlement_date=date(2026, 8, 31),
        reference=f"REF-{settlement_id}",
        created_at=datetime.now(
            timezone.utc,
        ),
    )


async def get_match_results_for_run(
    session,
    run_id: int,
) -> dict[str, MatchResultORM]:
    """Load all persisted match results for a run."""

    query = await session.execute(
        select(MatchResultORM)
        .where(
            MatchResultORM.run_id == run_id,
        )
        .order_by(
            MatchResultORM.settlement_id,
        )
    )

    return {
        result.settlement_id: result
        for result in query.scalars().all()
    }


@pytest.mark.asyncio
async def test_one_failed_record_does_not_abort_run():
    idempotency_key = unique_id(
        "TEST-FAILURE-ISOLATION",
    )

    async with SessionFactory() as session:
        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        s001 = unique_id("S001")
        s002 = unique_id("S002")
        s003 = unique_id("S003")

        settlements = [
            make_settlement(s001, run),
            make_settlement(s002, run),
            make_settlement(s003, run),
        ]

        session.add_all(settlements)
        await session.commit()

        service = ReconciliationService(
            session=session,
            resolver=FakeHybridResolver(
                failing_settlement_id=s002,
            ),
        )

        processed_run = await service.process_run(
            idempotency_key=idempotency_key,
            settlements=settlements,
        )

        assert (
            processed_run.status
            == ReconciliationState.COMPLETED.value
        )

        results = await get_match_results_for_run(
            session,
            processed_run.id,
        )

        assert len(results) == 3

        assert results[s001].status == "MATCHED_AI"
        assert results[s002].status == "FAILED"
        assert results[s003].status == "MATCHED_AI"


@pytest.mark.asyncio
async def test_llm_timeout_marks_record_failed_and_continues():
    idempotency_key = unique_id(
        "TEST-LLM-TIMEOUT-ISOLATION",
    )

    s001 = unique_id("S001")
    s002 = unique_id("S002")
    s003 = unique_id("S003")

    class TimeoutResolver:
        async def resolve(self, settlement):
            if settlement.settlement_id == s002:
                raise LLMTimeoutError(
                    "injected timeout",
                )

            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=[],
                confidence=0.0,
                evidence_codes=[
                    "test_success",
                ],
                reason="test resolution",
            )

    async with SessionFactory() as session:
        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        settlements = [
            make_settlement(s001, run),
            make_settlement(s002, run),
            make_settlement(s003, run),
        ]

        session.add_all(settlements)
        await session.commit()

        service = ReconciliationService(
            session=session,
            resolver=TimeoutResolver(),
        )

        result = await service.process_run(
            idempotency_key=idempotency_key,
            settlements=settlements,
        )

        assert (
            result.status
            == ReconciliationState.COMPLETED.value
        )

        results = await get_match_results_for_run(
            session,
            result.id,
        )

        assert len(results) == 3

        assert results[s001].status == "MATCHED_AI"
        assert results[s002].status == "FAILED"
        assert results[s003].status == "MATCHED_AI"


@pytest.mark.asyncio
async def test_llm_provider_failure_marks_record_failed_and_continues():
    idempotency_key = unique_id(
        "TEST-LLM-PROVIDER-ISOLATION",
    )

    s001 = unique_id("S001")
    s002 = unique_id("S002")
    s003 = unique_id("S003")

    class ProviderErrorResolver:
        async def resolve(self, settlement):
            if settlement.settlement_id == s002:
                raise LLMProviderError(
                    "injected provider failure",
                )

            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=[],
                confidence=0.0,
                evidence_codes=[
                    "test_success",
                ],
                reason="test resolution",
            )

    async with SessionFactory() as session:
        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        settlements = [
            make_settlement(s001, run),
            make_settlement(s002, run),
            make_settlement(s003, run),
        ]

        session.add_all(settlements)
        await session.commit()

        service = ReconciliationService(
            session=session,
            resolver=ProviderErrorResolver(),
        )

        result = await service.process_run(
            idempotency_key=idempotency_key,
            settlements=settlements,
        )

        assert (
            result.status
            == ReconciliationState.COMPLETED.value
        )

        results = await get_match_results_for_run(
            session,
            result.id,
        )

        assert len(results) == 3

        assert results[s001].status == "MATCHED_AI"
        assert results[s002].status == "FAILED"
        assert results[s003].status == "MATCHED_AI"


@pytest.mark.asyncio
async def test_unexpected_ai_failure_marks_record_failed_and_continues():
    idempotency_key = unique_id(
        "TEST-UNEXPECTED-AI-FAILURE",
    )

    s001 = unique_id("S001")
    s002 = unique_id("S002")
    s003 = unique_id("S003")

    class UnexpectedErrorResolver:
        async def resolve(self, settlement):
            if settlement.settlement_id == s002:
                raise ValueError(
                    "injected unexpected failure",
                )

            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=[],
                confidence=0.0,
                evidence_codes=[
                    "test_success",
                ],
                reason="test resolution",
            )

    async with SessionFactory() as session:
        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        settlements = [
            make_settlement(s001, run),
            make_settlement(s002, run),
            make_settlement(s003, run),
        ]

        session.add_all(settlements)
        await session.commit()

        service = ReconciliationService(
            session=session,
            resolver=UnexpectedErrorResolver(),
        )

        result = await service.process_run(
            idempotency_key=idempotency_key,
            settlements=settlements,
        )

        assert (
            result.status
            == ReconciliationState.COMPLETED.value
        )

        results = await get_match_results_for_run(
            session,
            result.id,
        )

        assert len(results) == 3

        assert results[s001].status == "MATCHED_AI"
        assert results[s002].status == "FAILED"
        assert results[s003].status == "MATCHED_AI"

@pytest.mark.asyncio
async def test_database_failure_rolls_back_record_and_continues():
    idempotency_key = unique_id(
        "TEST-DB-ROLLBACK"
    )

    s001 = unique_id("S001")
    s002 = unique_id("S002")
    s003 = unique_id("S003")

    class DatabaseFailureResolver:
        async def resolve(self, settlement):
            if settlement.settlement_id == s002:
                return HybridResolution(
                    settlement_id=settlement.settlement_id,
                    action=PolicyAction.AUTO_MATCH,
                    candidate_ids=[],
                    confidence=1.5,
                    evidence_codes=[
                        "injected_invalid_confidence"
                    ],
                    reason="injected database failure",
                )

            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=[],
                confidence=0.0,
                evidence_codes=[
                    "test_success"
                ],
                reason="test resolution",
            )

    async with SessionFactory() as session:
        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        settlements = [
            make_settlement(s001, run),
            make_settlement(s002, run),
            make_settlement(s003, run),
        ]

        session.add_all(settlements)
        await session.commit()

        service = ReconciliationService(
            session=session,
            resolver=DatabaseFailureResolver(),
        )

        result = await service.process_run(
            idempotency_key=idempotency_key,
            settlements=settlements,
        )

        assert (
            result.status
            == ReconciliationState.COMPLETED.value
        )

        results = await get_match_results_for_run(
            session,
            result.id,
        )

        assert len(results) == 3

        assert results[s001].status == "MATCHED_AI"
        assert results[s002].status == "FAILED"
        assert results[s003].status == "MATCHED_AI"

        assert (
            results[s002].confidence
            == 0.0
        )

        assert (
            results[s002].evidence["codes"]
            == ["record_processing_failed"]
        )

        # No invalid confidence result survived the rollback.
        assert all(
            result.confidence <= 1.0
            for result in results.values()
        )
        