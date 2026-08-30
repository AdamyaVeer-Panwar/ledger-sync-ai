from app.domain.enums import MatchStatus
from app.domain.reconciliation.rule_result import RuleMatchResult

from app.domain.models import MatchDecision
from app.domain.reconciliation.rule_result import (
    to_rule_match_result,
)

from app.domain.enums import MatchStatus
from app.domain.models import MatchDecision
from app.domain.reconciliation.rule_result import (
    to_rule_match_result,
)

def test_rule_match_result_represents_confident_match():
    result = RuleMatchResult(
        status=MatchStatus.MATCHED_RULE,
        candidate_ids=["L001"],
        confidence=1.0,
        evidence_codes=[
            "reference_exact",
            "amount_exact",
        ],
        is_confident=True,
    )

    assert result.status == MatchStatus.MATCHED_RULE
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 1.0
    assert result.evidence_codes == [
        "reference_exact",
        "amount_exact",
    ]
    assert result.is_confident is True


def test_rule_match_result_represents_uncertain_result():
    result = RuleMatchResult(
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        evidence_codes=["no_match"],
        is_confident=False,
    )

    assert result.status == MatchStatus.NO_MATCH
    assert result.candidate_ids == []
    assert result.is_confident is False


def test_rule_match_result_supports_multiple_candidates():
    result = RuleMatchResult(
        status=MatchStatus.HUMAN_REVIEW,
        candidate_ids=["L001", "L002"],
        confidence=0.0,
        evidence_codes=[
            "multiple_candidates",
        ],
        is_confident=False,
    )

    assert result.candidate_ids == [
        "L001",
        "L002",
    ]


def test_adapter_marks_rule_match_as_confident():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.MATCHED_RULE,
        ledger_id="L001",
        confidence=1.0,
        evidence=["amount_exact"],
        source="rule_exact",
    )

    result = to_rule_match_result(decision)

    assert result.candidate_ids == ["L001"]
    assert result.confidence == 1.0
    assert result.evidence_codes == [
        "amount_exact"
    ]
    assert result.is_confident is True


def test_adapter_marks_no_match_as_uncertain():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.NO_MATCH,
        ledger_id=None,
        confidence=0.0,
        evidence=["no_match"],
        source="rule_matcher",
    )

    result = to_rule_match_result(decision)

    assert result.candidate_ids == []
    assert result.is_confident is False


def test_adapter_converts_rule_match():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.MATCHED_RULE,
        ledger_id="L001",
        confidence=1.0,
        evidence=[
            "reference_exact",
            "amount_exact",
        ],
        source="rule_exact_reference_amount",
    )

    result = to_rule_match_result(decision)

    assert result.status == MatchStatus.MATCHED_RULE
    assert result.candidate_ids == ["L001"]
    assert result.confidence == 1.0
    assert result.evidence_codes == [
        "reference_exact",
        "amount_exact",
    ]
    assert result.is_confident is True


def test_adapter_converts_no_match_as_uncertain():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.NO_MATCH,
        ledger_id=None,
        confidence=0.0,
        evidence=["no_match"],
        source="rule_matcher",
    )

    result = to_rule_match_result(decision)

    assert result.status == MatchStatus.NO_MATCH
    assert result.candidate_ids == []
    assert result.confidence == 0.0
    assert result.evidence_codes == ["no_match"]
    assert result.is_confident is False


def test_adapter_converts_human_review_as_uncertain():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.HUMAN_REVIEW,
        ledger_id=None,
        confidence=0.0,
        evidence=[
            "amount_exact",
            "multiple_candidates",
        ],
        source="rule_exact_amount_merchant_date",
    )

    result = to_rule_match_result(decision)

    assert result.status == MatchStatus.HUMAN_REVIEW
    assert result.candidate_ids == []
    assert result.is_confident is False