from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.enums import LedgerEntryType, MatchStatus
from app.domain.models import LedgerRecord, MatchDecision, SettlementRecord
from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusionResult,
    FusionAgreement,
)
from app.domain.reconciliation.hybrid_resolver import HybridResolver
from app.domain.reconciliation.llm_verifier import (
    LLMVerificationResult,
    VerificationStatus,
)
from app.domain.reconciliation.policy import (
    PolicyAction,
    PolicyDecision,
)
from app.domain.reconciliation.rule_result import RuleMatchResult


def make_settlement() -> SettlementRecord:
    return SettlementRecord(
        settlement_id="S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date="2026-08-25",
        reference="UTR-001",
    )


def make_ledger() -> LedgerRecord:
    return LedgerRecord(
        ledger_id="L001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        transaction_date="2026-08-25",
        reference="UTR-001",
        entry_type=LedgerEntryType.PAYMENT,
    )


def make_orm_ledger() -> Mock:
    ledger = Mock()
    ledger.ledger_id = "L001"
    ledger.merchant_id = "M001"
    ledger.amount = "1000.00"
    ledger.currency = "INR"
    ledger.transaction_date = "2026-08-25"
    ledger.reference = "UTR-001"
    ledger.entry_type = LedgerEntryType.PAYMENT
    return ledger


def make_rule_decision() -> MatchDecision:
    return MatchDecision(
        settlement_id="S001",
        status=MatchStatus.MATCHED_RULE,
        candidate_ids=["L001"],
        confidence=1.0,
        evidence=["amount_exact"],
        source="rule_exact",
    )


def make_rule_result(
    *,
    status: MatchStatus,
    candidate_ids: list[str],
    confidence: float,
    is_confident: bool,
) -> RuleMatchResult:
    return RuleMatchResult(
        status=status,
        candidate_ids=candidate_ids,
        confidence=confidence,
        evidence_codes=["rule_evidence"],
        is_confident=is_confident,
    )


def make_ai_result() -> Mock:
    result = Mock()
    result.resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=0.94,
        evidence_codes=["amount_exact"],
    )
    result.usage.input_tokens = 100
    result.usage.output_tokens = 20
    result.usage.total_tokens = 120
    return result


def make_verification_result(
    *,
    status: VerificationStatus,
) -> LLMVerificationResult:
    return LLMVerificationResult(
        status=status,
        candidate_ids=["L001"],
        evidence_codes=["candidate_ids_valid"],
        reason="test verification",
    )


def make_fusion_result() -> EvidenceFusionResult:
    return EvidenceFusionResult(
        candidate_ids=["L001"],
        agreement=FusionAgreement.LLM_SUPPORTED,
        confidence=0.94,
        evidence_codes=[
            "amount_exact",
            "candidate_ids_valid",
        ],
    )


def make_policy_decision() -> PolicyDecision:
    return PolicyDecision(
        action=PolicyAction.AUTO_MATCH,
        candidate_ids=["L001"],
        confidence=0.94,
        evidence_codes=[
            "amount_exact",
            "candidate_ids_valid",
        ],
        reason="verified LLM-supported match",
    )


@pytest.mark.asyncio
async def test_confident_rule_match_bypasses_llm():
    retriever = Mock()

    retriever.retrieve = AsyncMock(
        return_value=[
            make_orm_ledger(),
        ]
    )

    rule_matcher = Mock()
    rule_matcher.match.return_value = make_rule_decision()

    llm_resolver = Mock()
    llm_resolver.resolve = AsyncMock()

    verifier = Mock()
    fusion = Mock()
    policy = Mock()

    resolver = HybridResolver(
        rule_matcher=rule_matcher,
        candidate_retriever=retriever,
        llm_resolver=llm_resolver,
        verifier=verifier,
        fusion=fusion,
        policy=policy,
    )

    result = await resolver.resolve(
        make_settlement()
    )

    assert result.action == PolicyAction.AUTO_MATCH
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 1.0

    llm_resolver.resolve.assert_not_awaited()
    verifier.verify.assert_not_called()
    fusion.fuse.assert_not_called()
    policy.evaluate.assert_not_called()


@pytest.mark.asyncio
async def test_uncertain_rule_result_calls_llm():
    retriever = Mock()

    retriever.retrieve = AsyncMock(
        return_value=[
            make_orm_ledger(),
        ]
    )

    rule_matcher = Mock()

    rule_matcher.match.return_value = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        evidence=["no_match"],
        source="rule_matcher",
    )

    llm_resolver = Mock()
    llm_resolver.resolve = AsyncMock(
        return_value=make_ai_result()
    )

    verifier = Mock()
    verifier.verify.return_value = make_verification_result(
        status=VerificationStatus.VERIFIED
    )

    fusion = Mock()
    fusion.fuse.return_value = make_fusion_result()

    policy = Mock()
    policy.evaluate.return_value = make_policy_decision()

    resolver = HybridResolver(
        rule_matcher=rule_matcher,
        candidate_retriever=retriever,
        llm_resolver=llm_resolver,
        verifier=verifier,
        fusion=fusion,
        policy=policy,
    )

    result = await resolver.resolve(
        make_settlement()
    )

    assert result.action == PolicyAction.AUTO_MATCH
    assert result.candidate_ids == ["L001"]

    llm_resolver.resolve.assert_awaited_once()
    verifier.verify.assert_called_once()
    fusion.fuse.assert_called_once()
    policy.evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_llm_resolution_is_verified_before_fusion():
    retriever = Mock()

    retriever.retrieve = AsyncMock(
        return_value=[
            make_orm_ledger(),
        ]
    )

    rule_matcher = Mock()

    rule_matcher.match.return_value = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        evidence=["no_match"],
        source="rule_matcher",
    )

    llm_resolver = Mock()
    ai_result = make_ai_result()

    llm_resolver.resolve = AsyncMock(
        return_value=ai_result
    )

    verifier = Mock()
    verification = make_verification_result(
        status=VerificationStatus.VERIFIED
    )
    verifier.verify.return_value = verification

    fusion = Mock()
    fusion.fuse.return_value = make_fusion_result()

    policy = Mock()
    policy.evaluate.return_value = make_policy_decision()

    resolver = HybridResolver(
        rule_matcher=rule_matcher,
        candidate_retriever=retriever,
        llm_resolver=llm_resolver,
        verifier=verifier,
        fusion=fusion,
        policy=policy,
    )

    await resolver.resolve(
        make_settlement()
    )

    verifier.verify.assert_called_once_with(
        settlement=make_settlement(),
        candidates=[make_ledger()],
        resolution=ai_result.resolution,
    )

    fusion.fuse.assert_called_once()

    fusion_args = fusion.fuse.call_args.args

    assert isinstance(
        fusion_args[0],
        RuleMatchResult,
    )
    assert fusion_args[1] == ai_result.resolution
    assert fusion_args[2] == verification


@pytest.mark.asyncio
async def test_verifier_rejection_reaches_policy_as_conflict():
    retriever = Mock()

    retriever.retrieve = AsyncMock(
        return_value=[
            make_orm_ledger(),
        ]
    )

    rule_matcher = Mock()

    rule_matcher.match.return_value = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        evidence=["no_match"],
        source="rule_matcher",
    )

    llm_resolver = Mock()
    llm_resolver.resolve = AsyncMock(
        return_value=make_ai_result()
    )

    verifier = Mock()
    verifier.verify.return_value = make_verification_result(
        status=VerificationStatus.REJECTED
    )

    fusion_result = EvidenceFusionResult(
        candidate_ids=["L001"],
        agreement=FusionAgreement.CONFLICT,
        confidence=0.0,
        evidence_codes=[
            "llm_verification_rejected",
        ],
    )

    fusion = Mock()
    fusion.fuse.return_value = fusion_result

    policy_decision = PolicyDecision(
        action=PolicyAction.HUMAN_REVIEW,
        candidate_ids=["L001"],
        confidence=0.0,
        evidence_codes=[
            "llm_verification_rejected",
        ],
        reason="rules and LLM evidence conflict",
    )

    policy = Mock()
    policy.evaluate.return_value = policy_decision

    resolver = HybridResolver(
        rule_matcher=rule_matcher,
        candidate_retriever=retriever,
        llm_resolver=llm_resolver,
        verifier=verifier,
        fusion=fusion,
        policy=policy,
    )

    result = await resolver.resolve(
        make_settlement()
    )

    assert result.action == PolicyAction.HUMAN_REVIEW
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_candidate_retriever_output_is_converted_to_domain_records():
    retriever = Mock()

    retriever.retrieve = AsyncMock(
        return_value=[
            make_orm_ledger(),
        ]
    )

    rule_matcher = Mock()
    rule_matcher.match.return_value = make_rule_decision()

    llm_resolver = Mock()
    llm_resolver.resolve = AsyncMock()

    verifier = Mock()
    fusion = Mock()
    policy = Mock()

    resolver = HybridResolver(
        rule_matcher=rule_matcher,
        candidate_retriever=retriever,
        llm_resolver=llm_resolver,
        verifier=verifier,
        fusion=fusion,
        policy=policy,
    )

    await resolver.resolve(
        make_settlement()
    )

    rule_call = rule_matcher.match.call_args

    candidates = rule_call.kwargs["candidates"]

    assert len(candidates) == 1
    assert isinstance(
        candidates[0],
        LedgerRecord,
    )
    assert candidates[0].ledger_id == "L001"