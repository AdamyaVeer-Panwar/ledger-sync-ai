import pytest
from pydantic import ValidationError

from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)


def test_ai_resolution_accepts_valid_match():
    result = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=0.94,
        evidence_codes=[
            "EXACT_AMOUNT",
            "SAME_MERCHANT",
        ],
    )

    assert result.decision == AIResolutionDecision.MATCH
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 0.94
    assert result.evidence_codes == [
        "EXACT_AMOUNT",
        "SAME_MERCHANT",
    ]


def test_ai_resolution_allows_no_match_without_candidate():
    result = AIResolution(
        decision=AIResolutionDecision.NO_MATCH,
        candidate_ids=[],
        confidence=0.12,
        evidence_codes=["MERCHANT_MISMATCH"],
    )

    assert result.decision == AIResolutionDecision.NO_MATCH
    assert result.candidate_ids == []


def test_ai_resolution_allows_ambiguous_without_candidate():
    result = AIResolution(
        decision=AIResolutionDecision.AMBIGUOUS,
        candidate_ids=[],
        confidence=0.51,
        evidence_codes=[
            "MULTIPLE_PLAUSIBLE_CANDIDATES"
        ],
    )

    assert result.decision == AIResolutionDecision.AMBIGUOUS
    assert result.candidate_ids == []


def test_ai_resolution_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        AIResolution(
            decision=AIResolutionDecision.MATCH,
            candidate_ids=["L001"],
            confidence=1.5,
        )


def test_ai_resolution_rejects_invalid_decision():
    with pytest.raises(ValidationError):
        AIResolution(
            decision="MAYBE",
            candidate_ids=["L001"],
            confidence=0.5,
        )


def test_match_requires_candidate_ids():
    with pytest.raises(
        ValidationError,
        match="candidate_ids is required for MATCH",
    ):
        AIResolution(
            decision=AIResolutionDecision.MATCH,
            candidate_ids=[],
            confidence=0.95,
        )


def test_no_match_requires_empty_candidate_ids():
    with pytest.raises(
        ValidationError,
        match="candidate_ids must be empty for NO_MATCH",
    ):
        AIResolution(
            decision=AIResolutionDecision.NO_MATCH,
            candidate_ids=["L001"],
            confidence=0.10,
        )


def test_candidate_ids_are_required_in_payload():
    with pytest.raises(ValidationError):
        AIResolution(
            decision=AIResolutionDecision.NO_MATCH,
            confidence=0.10,
        )