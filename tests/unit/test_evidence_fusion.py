from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.enums import MatchStatus
from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusion,
    FusionAgreement,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerificationResult,
    VerificationStatus,
)
from app.domain.reconciliation.rule_result import (
    RuleMatchResult,
)




def make_rule_result(
    *,
    status: MatchStatus,
    candidate_ids: list[str],
    confidence: float,
    is_confident: bool,
):
    return RuleMatchResult(
        status=status,
        candidate_ids=candidate_ids,
        confidence=confidence,
        evidence_codes=["rule_evidence"],
        is_confident=is_confident,
    )


def make_ai_result(
    *,
    decision: AIResolutionDecision,
    candidate_ids: list[str],
    confidence: float,
):
    return AIResolution(
        decision=decision,
        candidate_ids=candidate_ids,
        confidence=confidence,
        evidence_codes=["llm_evidence"],
    )


def make_verification_result(
    *,
    status: VerificationStatus,
    candidate_ids: list[str],
    evidence_codes: list[str] | None = None,
):
    return LLMVerificationResult(
        status=status,
        candidate_ids=candidate_ids,
        evidence_codes=(
            evidence_codes
            if evidence_codes is not None
            else ["verification_evidence"]
        ),
        reason="test",
    )


def test_fusion_detects_strong_agreement():
    rules = make_rule_result(
        status=MatchStatus.MATCHED_RULE,
        candidate_ids=["L001"],
        confidence=1.0,
        is_confident=True,
    )

    llm = make_ai_result(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=0.96,
    )

    verification = make_verification_result(
        status=VerificationStatus.VERIFIED,
        candidate_ids=["L001"],
    )

    result = EvidenceFusion().fuse(
        rules,
        llm,
        verification,
    )

    assert (
        result.agreement
        == FusionAgreement.STRONG_AGREEMENT
    )

    assert result.candidate_ids == ["L001"]

    assert result.confidence == 1.0


def test_fusion_detects_verified_llm_supported_match():
    rules = make_rule_result(
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        is_confident=False,
    )

    llm = make_ai_result(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=0.91,
    )

    verification = make_verification_result(
        status=VerificationStatus.VERIFIED,
        candidate_ids=["L001"],
    )

    result = EvidenceFusion().fuse(
        rules,
        llm,
        verification,
    )

    assert (
        result.agreement
        == FusionAgreement.LLM_SUPPORTED
    )

    assert result.candidate_ids == ["L001"]


def test_rejected_llm_proposal_becomes_conflict():
    rules = make_rule_result(
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        is_confident=False,
    )

    llm = make_ai_result(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=1.0,
    )

    verification = make_verification_result(
        status=VerificationStatus.REJECTED,
        candidate_ids=["L001"],
        evidence_codes=[
            "amount_mismatch",
        ],
    )

    result = EvidenceFusion().fuse(
        rules,
        llm,
        verification,
    )

    assert (
        result.agreement
        == FusionAgreement.CONFLICT
    )

    assert result.confidence == 0.0

    assert (
        "llm_verification_rejected"
        in result.evidence_codes
    )


def test_unverified_llm_proposal_does_not_become_match():
    rules = make_rule_result(
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        is_confident=False,
    )

    llm = make_ai_result(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001", "L002"],
        confidence=0.99,
    )

    verification = make_verification_result(
        status=VerificationStatus.UNVERIFIED,
        candidate_ids=["L001", "L002"],
    )

    result = EvidenceFusion().fuse(
        rules,
        llm,
        verification,
    )

    assert (
        result.agreement
        == FusionAgreement.CONFLICT
    )

    assert result.confidence == 0.0

    assert (
        "llm_verification_unverified"
        in result.evidence_codes
    )


def test_fusion_detects_ambiguity():
    rules = make_rule_result(
        status=MatchStatus.HUMAN_REVIEW,
        candidate_ids=[],
        confidence=0.0,
        is_confident=False,
    )

    llm = make_ai_result(
        decision=AIResolutionDecision.AMBIGUOUS,
        candidate_ids=["L001", "L002"],
        confidence=0.55,
    )

    verification = make_verification_result(
        status=VerificationStatus.UNVERIFIED,
        candidate_ids=["L001", "L002"],
    )

    result = EvidenceFusion().fuse(
        rules,
        llm,
        verification,
    )

    assert (
        result.agreement
        == FusionAgreement.AMBIGUOUS
    )

    assert result.candidate_ids == [
        "L001",
        "L002",
    ]

def test_deterministic_ambiguity_cannot_be_overridden_by_llm():
    fusion = EvidenceFusion()

    rule_result = RuleMatchResult(
        status=MatchStatus.HUMAN_REVIEW,
        candidate_ids=[
            "L001",
            "L002",
        ],
        confidence=0.0,
        evidence_codes=[
            "multiple_candidates",
        ],
        is_confident=False,
    )

    ai_result = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=[
            "L001",
        ],
        confidence=0.99,
        evidence_codes=[
            "llm_selected_candidate",
        ],
    )

    verification_result = LLMVerificationResult(
        status=VerificationStatus.VERIFIED,
        candidate_ids=[
            "L001",
        ],
        evidence_codes=[
            "candidate_ids_valid",
        ],
        reason="candidate is individually valid",
    )

    result = fusion.fuse(
        rule_result,
        ai_result,
        verification_result,
    )

    assert result.agreement == FusionAgreement.AMBIGUOUS

    assert result.candidate_ids == [
        "L001",
        "L002",
    ]

    assert result.confidence == 0.0

    assert (
        "deterministic_ambiguity"
        in result.evidence_codes
    )