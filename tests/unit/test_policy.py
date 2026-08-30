from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusionResult,
    FusionAgreement,
)
from app.domain.reconciliation.policy import (
    PolicyAction,
    PolicyEngine,
)


def make_fusion_result(
    *,
    agreement: FusionAgreement,
    confidence: float,
    candidate_ids: list[str] | None = None,
):
    return EvidenceFusionResult(
        candidate_ids=(
            candidate_ids
            if candidate_ids is not None
            else ["L001"]
        ),
        agreement=agreement,
        confidence=confidence,
        evidence_codes=["test_evidence"],
    )


def test_strong_agreement_auto_matches():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.STRONG_AGREEMENT,
        confidence=0.50,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.AUTO_MATCH
    assert decision.candidate_ids == ["L001"]


def test_verified_llm_supported_result_auto_matches():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.LLM_SUPPORTED,
        confidence=0.40,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.AUTO_MATCH


def test_ambiguous_result_requires_human_review():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.AMBIGUOUS,
        confidence=0.95,
        candidate_ids=[
            "L001",
            "L002",
        ],
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.HUMAN_REVIEW
    assert decision.candidate_ids == [
        "L001",
        "L002",
    ]


def test_conflict_with_candidate_requires_human_review():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.CONFLICT,
        confidence=1.0,
        candidate_ids=["L001"],
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.HUMAN_REVIEW
    assert decision.confidence == 0.0


def test_conflict_without_candidate_returns_no_match():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.CONFLICT,
        confidence=0.0,
        candidate_ids=[],
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.NO_MATCH
    assert decision.candidate_ids == []
    assert decision.confidence == 0.0


def test_high_llm_confidence_cannot_override_conflict():
    policy = PolicyEngine()

    result = make_fusion_result(
        agreement=FusionAgreement.CONFLICT,
        confidence=1.0,
        candidate_ids=["L001"],
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.HUMAN_REVIEW
    assert decision.action != PolicyAction.AUTO_MATCH