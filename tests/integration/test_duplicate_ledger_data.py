from datetime import date, datetime, timezone
from decimal import Decimal
import uuid

import pytest

from app.db.models import LedgerORM, SettlementORM
from app.db.session import SessionFactory
from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.models import SettlementRecord
from app.domain.reconciliation.evidence_fusion import EvidenceFusion
from app.domain.reconciliation.hybrid_resolver import HybridResolver
from app.domain.reconciliation.llm_verifier import LLMVerifier
from app.domain.reconciliation.policy import (
    PolicyAction,
    PolicyEngine,
)
from app.domain.reconciliation.rule_matcher import RuleMatcher
from app.repositories.candidate_retriever import CandidateRetriever
from app.repositories.run_repository import RunRepository


def unique_id(prefix: str) -> str:
    """Return a unique identifier for repeatable integration tests."""
    return f"{prefix}-{uuid.uuid4().hex}"


class FakeLLMResult:
    """Minimal result object compatible with HybridResolver."""

    def __init__(
        self,
        resolution: AIResolution,
    ) -> None:
        self.resolution = resolution


class FakeLLMResolver:
    """
    Deterministic LLM test double.

    The fake LLM intentionally selects one candidate from an
    ambiguous duplicate candidate set.

    The hybrid pipeline must prevent that proposal from becoming
    an automatic financial decision.
    """

    def __init__(
        self,
        candidate_id: str,
    ) -> None:
        self.candidate_id = candidate_id

    async def resolve(
        self,
        settlement: SettlementRecord,
        candidates: list,
    ) -> FakeLLMResult:
        return FakeLLMResult(
            resolution=AIResolution(
                decision=AIResolutionDecision.MATCH,
                candidate_ids=[
                    self.candidate_id,
                ],
                confidence=0.99,
                evidence_codes=[
                    "llm_selected_candidate",
                ],
            )
        )


@pytest.mark.asyncio
async def test_duplicate_ledger_candidates_require_human_review():
    """
    Two indistinguishable ledger records must not be converted
    into an automatic match merely because the LLM selects one.
    """

    unique_suffix = uuid.uuid4().hex

    idempotency_key = (
        f"TEST-DUPLICATE-LEDGER-RUN-{unique_suffix}"
    )

    settlement_id = (
        f"TEST-DUPLICATE-SETTLEMENT-{unique_suffix}"
    )

    ledger_1_id = (
        f"TEST-DUPLICATE-L001-{unique_suffix}"
    )

    ledger_2_id = (
        f"TEST-DUPLICATE-L002-{unique_suffix}"
    )

    # These values must also be unique because CandidateRetriever
    # searches by merchant + currency + amount + date + reference.
    merchant_id = (
        f"M-DUPLICATE-{unique_suffix}"
    )

    reference = (
        f"UTR-DUPLICATE-{unique_suffix}"
    )

    async with SessionFactory() as session:
        # ---------------------------------------------------------
        # 1. Create reconciliation run.
        # ---------------------------------------------------------

        run_repository = RunRepository(session)

        run = await run_repository.create(
            idempotency_key=idempotency_key,
        )

        await session.flush()

        run_id = run.id

        # ---------------------------------------------------------
        # 2. Create settlement.
        # ---------------------------------------------------------

        settlement = SettlementORM(
            settlement_id=settlement_id,
            run_id=run_id,
            merchant_id=merchant_id,
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 31),
            reference=reference,
            created_at=datetime.now(
                timezone.utc
            ),
        )

        # ---------------------------------------------------------
        # 3. Create two indistinguishable ledger records.
        # ---------------------------------------------------------

        ledger_1 = LedgerORM(
            ledger_id=ledger_1_id,
            merchant_id=merchant_id,
            amount=Decimal("1000.00"),
            currency="INR",
            transaction_date=date(2026, 8, 31),
            reference=reference,
            entry_type="PAYMENT",
            created_at=datetime.now(
                timezone.utc
            ),
        )

        ledger_2 = LedgerORM(
            ledger_id=ledger_2_id,
            merchant_id=merchant_id,
            amount=Decimal("1000.00"),
            currency="INR",
            transaction_date=date(2026, 8, 31),
            reference=reference,
            entry_type="PAYMENT",
            created_at=datetime.now(
                timezone.utc
            ),
        )

        session.add_all(
            [
                settlement,
                ledger_1,
                ledger_2,
            ]
        )

        await session.commit()

        # ---------------------------------------------------------
        # 4. Convert settlement to a domain object.
        # ---------------------------------------------------------

        settlement_domain = SettlementRecord(
            settlement_id=settlement_id,
            merchant_id=merchant_id,
            amount=Decimal("1000.00"),
            currency="INR",
            settlement_date=date(2026, 8, 31),
            reference=reference,
        )

        # ---------------------------------------------------------
        # 5. Build the real hybrid pipeline.
        # ---------------------------------------------------------

        candidate_retriever = CandidateRetriever(
            session
        )

        hybrid_resolver = HybridResolver(
            rule_matcher=RuleMatcher(),
            candidate_retriever=candidate_retriever,
            llm_resolver=FakeLLMResolver(
                candidate_id=ledger_1_id,
            ),
            verifier=LLMVerifier(),
            fusion=EvidenceFusion(),
            policy=PolicyEngine(),
        )

        # ---------------------------------------------------------
        # 6. Resolve through the actual hybrid pipeline.
        # ---------------------------------------------------------

        result = await hybrid_resolver.resolve(
            settlement=settlement_domain
        )

        # ---------------------------------------------------------
        # 7. Reliability invariants.
        # ---------------------------------------------------------

        # The deterministic layer found multiple indistinguishable
        # candidates, so automatic authorization is forbidden.
        assert result.action == PolicyAction.HUMAN_REVIEW

        assert result.action != PolicyAction.AUTO_MATCH

        # Both duplicate candidates must remain visible as the
        # unresolved candidate set.
        assert set(result.candidate_ids) == {
            ledger_1_id,
            ledger_2_id,
        }

        # The LLM must not collapse the deterministic ambiguity.
        assert (
            result.candidate_ids
            != [ledger_1_id]
        )