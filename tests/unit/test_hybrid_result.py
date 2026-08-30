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
    )

    assert result.settlement_id == "S001"
    assert result.action == PolicyAction.AUTO_MATCH
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 0.98


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
    )

    assert result.action == PolicyAction.HUMAN_REVIEW
    assert result.candidate_ids == [
        "L001",
        "L002",
    ]


def test_hybrid_resolution_represents_no_match():
    result = HybridResolution(
        settlement_id="S003",
        action=PolicyAction.NO_MATCH,
        candidate_ids=[],
        confidence=0.20,
        evidence_codes=["no_valid_reconciliation"],
        reason="evidence below policy threshold",
    )

    assert result.action == PolicyAction.NO_MATCH
    assert result.candidate_ids == []