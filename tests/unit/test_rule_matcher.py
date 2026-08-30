from datetime import date
from decimal import Decimal

from app.domain.enums import (
    LedgerEntryType,
    MatchStatus,
)
from app.domain.models import (
    LedgerRecord,
    SettlementRecord,
)
from app.domain.reconciliation.rule_matcher import (
    RuleMatcher,
)


def make_settlement(
    *,
    settlement_id: str = "S000001",
    merchant_id: str = "M001",
    amount: str = "1000.00",
    settlement_date: date = date(2026, 8, 25),
    reference: str | None = "UTR-100001",
) -> SettlementRecord:
    return SettlementRecord(
        settlement_id=settlement_id,
        merchant_id=merchant_id,
        amount=Decimal(amount),
        currency="INR",
        settlement_date=settlement_date,
        reference=reference,
    )


def make_ledger(
    *,
    ledger_id: str = "L000001",
    merchant_id: str = "M001",
    amount: str = "1000.00",
    transaction_date: date = date(2026, 8, 25),
    reference: str | None = "UTR-100001",
) -> LedgerRecord:
    return LedgerRecord(
        ledger_id=ledger_id,
        merchant_id=merchant_id,
        amount=Decimal(amount),
        currency="INR",
        transaction_date=transaction_date,
        reference=reference,
        entry_type=LedgerEntryType.PAYMENT,
    )


def test_exact_reference_and_amount_match():
    matcher = RuleMatcher()

    settlement = make_settlement()
    ledger = make_ledger()

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L000001"]
    assert decision.confidence == 1.0
    assert decision.source == "rule_exact_reference_amount"
    assert decision.evidence == [
        "reference_exact",
        "amount_exact",
    ]


def test_exact_amount_merchant_and_date_match():
    matcher = RuleMatcher()

    settlement = make_settlement(
        reference="UTR-SETTLEMENT",
    )

    ledger = make_ledger(
        reference="DIFFERENT-REFERENCE",
    )

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L000001"]
    assert decision.confidence == 0.95
    assert decision.source == (
        "rule_exact_amount_merchant_date"
    )
    assert decision.evidence == [
        "amount_exact",
        "merchant_exact",
        "date_exact",
    ]


def test_amount_tolerance_and_date_window_match():
    matcher = RuleMatcher()

    settlement = make_settlement(
        amount="1000.00",
        settlement_date=date(2026, 8, 25),
        reference="UTR-SETTLEMENT",
    )

    ledger = make_ledger(
        amount="999.98",
        transaction_date=date(2026, 8, 27),
        reference="DIFFERENT-REFERENCE",
    )

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L000001"]
    assert decision.confidence == 0.85
    assert decision.source == (
        "rule_amount_tolerance_date_window"
    )
    assert decision.evidence == [
        "amount_within_tolerance",
        "merchant_exact",
        "date_within_window",
    ]


def test_wrong_merchant_returns_no_match():
    matcher = RuleMatcher()

    settlement = make_settlement(
        merchant_id="M001",
    )

    ledger = make_ledger(
        merchant_id="M002",
    )

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.NO_MATCH
    assert decision.candidate_ids == []
    assert decision.confidence == 0.0
    assert decision.source == "rule_matcher"
    assert decision.evidence == ["no_match"]


def test_duplicate_candidates_return_human_review():
    matcher = RuleMatcher()

    settlement = make_settlement()

    ledger_1 = make_ledger(
        ledger_id="L000001",
    )

    ledger_2 = make_ledger(
        ledger_id="L000002",
    )

    decision = matcher.match(
        settlement,
        [ledger_1, ledger_2],
    )

    assert decision.status == MatchStatus.HUMAN_REVIEW
    assert decision.candidate_ids == [
        "L000001",
        "L000002",
    ]
    assert decision.confidence == 0.0
    assert decision.source == (
        "rule_exact_reference_amount"
    )
    assert "multiple_candidates" in decision.evidence


def test_missing_reference_can_match_by_amount_merchant_and_date():
    matcher = RuleMatcher()

    settlement = make_settlement(
        reference=None,
    )

    ledger = make_ledger(
        reference=None,
    )

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L000001"]
    assert decision.confidence == 0.95
    assert decision.source == (
        "rule_exact_amount_merchant_date"
    )


def test_ambiguous_tolerance_candidates_return_human_review():
    matcher = RuleMatcher()

    settlement = make_settlement(
        reference="UNKNOWN",
    )

    ledger_1 = make_ledger(
        ledger_id="L000001",
        amount="999.99",
        transaction_date=date(2026, 8, 24),
        reference="DIFFERENT-1",
    )

    ledger_2 = make_ledger(
        ledger_id="L000002",
        amount="1000.01",
        transaction_date=date(2026, 8, 26),
        reference="DIFFERENT-2",
    )

    decision = matcher.match(
        settlement,
        [ledger_1, ledger_2],
    )

    assert decision.status == MatchStatus.HUMAN_REVIEW
    assert decision.candidate_ids == [
        "L000001",
        "L000002",
    ]
    assert decision.confidence == 0.0
    assert decision.source == (
        "rule_amount_tolerance_date_window"
    )
    assert "multiple_candidates" in decision.evidence


def test_no_candidates_returns_no_match():
    matcher = RuleMatcher()

    settlement = make_settlement()

    decision = matcher.match(
        settlement,
        [],
    )

    assert decision.status == MatchStatus.NO_MATCH
    assert decision.candidate_ids == []
    assert decision.confidence == 0.0
    assert decision.source == "rule_matcher"
    assert decision.evidence == [
        "no_candidates",
    ]


def test_normalized_reference_match():
    matcher = RuleMatcher()

    settlement = make_settlement(
        reference="UTR100007",
        settlement_date=date(2026, 8, 25),
    )

    ledger = make_ledger(
        reference="UTR-100007",
        transaction_date=date(2026, 8, 30),
    )

    decision = matcher.match(
        settlement,
        [ledger],
    )

    assert decision.status == MatchStatus.MATCHED_RULE
    assert decision.candidate_ids == ["L000001"]
    assert decision.confidence == 0.90
    assert decision.source == (
        "rule_normalized_reference_amount"
    )
    assert decision.evidence == [
        "reference_normalized",
        "amount_exact",
    ]