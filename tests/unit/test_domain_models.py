from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.enums import (
    LedgerEntryType,
    MatchStatus,
)
from app.domain.models import (
    LedgerRecord,
    MatchDecision,
    SettlementRecord,
)


def test_settlement_record_accepts_valid_data():
    settlement = SettlementRecord(
        settlement_id="S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date=date(2026, 8, 26),
        reference="UTR123",
    )

    assert settlement.amount == 1000
    assert settlement.reference == "UTR123"


def test_settlement_reference_can_be_missing():
    settlement = SettlementRecord(
        settlement_id="S002",
        merchant_id="M001",
        amount="500.00",
        currency="INR",
        settlement_date=date(2026, 8, 26),
    )

    assert settlement.reference is None


def test_settlement_rejects_non_positive_amount():
    with pytest.raises(ValidationError):
        SettlementRecord(
            settlement_id="S003",
            merchant_id="M001",
            amount="0",
            currency="INR",
            settlement_date=date(2026, 8, 26),
        )


def test_match_decision_can_represent_rule_match():
    decision = MatchDecision(
        settlement_id="S001",
        status=MatchStatus.MATCHED_RULE,
        candidate_ids=["L001"],
        confidence=1.0,
        evidence=[
            "exact_reference",
            "exact_amount",
        ],
        source="rule_engine",
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L001"]
    assert decision.confidence == 1.0


def test_match_decision_can_represent_multiple_candidates():
    decision = MatchDecision(
        settlement_id="S002",
        status=MatchStatus.HUMAN_REVIEW,
        candidate_ids=[
            "L001",
            "L002",
        ],
        confidence=0.0,
        evidence=[
            "multiple_candidates",
        ],
        source="rule_engine",
    )

    assert decision.status == MatchStatus.HUMAN_REVIEW
    assert decision.candidate_ids == [
        "L001",
        "L002",
    ]


def test_match_decision_can_represent_no_match():
    decision = MatchDecision(
        settlement_id="S003",
        status=MatchStatus.NO_MATCH,
        candidate_ids=[],
        confidence=0.0,
        evidence=[
            "no_match",
        ],
        source="rule_engine",
    )

    assert decision.status == MatchStatus.NO_MATCH
    assert decision.candidate_ids == []


def test_ledger_record_supports_refund_entry():
    ledger = LedgerRecord(
        ledger_id="L001",
        merchant_id="M001",
        amount="100.00",
        currency="INR",
        transaction_date=date(2026, 8, 25),
        reference="REF001",
        entry_type=LedgerEntryType.REFUND,
    )

    assert ledger.ledger_id == "L001"
    assert ledger.entry_type == LedgerEntryType.REFUND