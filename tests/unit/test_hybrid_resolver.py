from app.domain.reconciliation.hybrid_result import (
    HybridResolution,
)
from app.domain.reconciliation.policy import (
    PolicyAction,
)


def test_hybrid_resolution_represents_auto_match():
    result = HybridResolution(
        settlement_id="S001",
        action=PolicyAction.AUTO_MATCH,
        candidate_ids=["L001"],
        confidence=0.98,
        evidence_codes=[
            "amount_exact",
            "reference_exact",
        ],
        reason="strong deterministic agreement",
        llm_invoked=False,
    )

    assert result.action == PolicyAction.AUTO_MATCH
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 0.98
    assert result.llm_invoked is False


def test_hybrid_resolution_represents_human_review():
    result = HybridResolution(
        settlement_id="S002",
        action=PolicyAction.HUMAN_REVIEW,
        candidate_ids=["L001", "L002"],
        confidence=0.75,
        evidence_codes=[
            "multiple_plausible_candidates",
        ],
        reason="insufficient evidence for auto-match",
        llm_invoked=False,
    )

    assert result.action == PolicyAction.HUMAN_REVIEW
    assert result.candidate_ids == [
        "L001",
        "L002",
    ]
    assert result.llm_invoked is False


def test_hybrid_resolution_represents_no_match():
    result = HybridResolution(
        settlement_id="S003",
        action=PolicyAction.NO_MATCH,
        candidate_ids=[],
        confidence=0.20,
        evidence_codes=[
            "no_valid_reconciliation",
        ],
        reason="evidence below policy threshold",
        llm_invoked=False,
    )

    assert result.action == PolicyAction.NO_MATCH
    assert result.candidate_ids == []
    assert result.llm_invoked is False


def test_hybrid_resolution_records_llm_invocation():
    result = HybridResolution(
        settlement_id="S004",
        action=PolicyAction.AUTO_MATCH,
        candidate_ids=["L004"],
        confidence=0.91,
        evidence_codes=[
            "llm_verified",
        ],
        reason=(
            "LLM proposal passed deterministic "
            "verification"
        ),
        llm_invoked=True,
    )

    assert result.llm_invoked is True