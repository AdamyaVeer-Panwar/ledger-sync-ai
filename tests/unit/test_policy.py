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
    agreement,
    confidence,
):
    return EvidenceFusionResult(
        candidate_ids=["L001"],
        agreement=agreement,
        confidence=confidence,
        evidence_codes=["test_evidence"],
    )


def test_high_confidence_strong_agreement_auto_matches():
    policy = PolicyEngine(
        high_threshold=0.90,
        medium_threshold=0.70,
    )

    result = make_fusion_result(
        agreement=FusionAgreement.STRONG_AGREEMENT,
        confidence=0.95,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.AUTO_MATCH
    assert decision.candidate_ids == ["L001"]


def test_medium_confidence_requires_human_review():
    policy = PolicyEngine(
        high_threshold=0.90,
        medium_threshold=0.70,
    )

    result = make_fusion_result(
        agreement=FusionAgreement.LLM_SUPPORTED,
        confidence=0.80,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.HUMAN_REVIEW


def test_low_confidence_returns_no_match():
    policy = PolicyEngine(
        high_threshold=0.90,
        medium_threshold=0.70,
    )

    result = make_fusion_result(
        agreement=FusionAgreement.LLM_SUPPORTED,
        confidence=0.40,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.NO_MATCH


def test_conflict_never_auto_matches():
    policy = PolicyEngine(
        high_threshold=0.90,
        medium_threshold=0.70,
    )

    result = make_fusion_result(
        agreement=FusionAgreement.CONFLICT,
        confidence=1.0,
    )

    decision = policy.evaluate(result)

    assert decision.action == PolicyAction.HUMAN_REVIEW


def test_invalid_thresholds_are_rejected():
    try:
        PolicyEngine(
            high_threshold=0.60,
            medium_threshold=0.80,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected invalid threshold configuration"
    )