import random
from datetime import date, timedelta
from decimal import Decimal

from app.domain.enums import LedgerEntryType
from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext
from app.domain.synthetic.scenarios import (
    generate_corrupted_reference,
    generate_date_lag,
    generate_duplicate,
    generate_exact_match,
    generate_missing_ledger,
    generate_missing_reference,
    generate_multiple_candidates,
    generate_partial_refund,
    generate_rounding_difference,
    generate_wrong_merchant,
)


def test_scenario_context():
    context = ScenarioContext(
        settlement_id="S000001",
        ledger_id="L000001",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    assert context.settlement_id == "S000001"
    assert context.ledger_id == "L000001"
    assert context.base_date == date(2026, 8, 25)


def test_exact_match_has_correct_ground_truth():
    context = ScenarioContext(
        settlement_id="S000001",
        ledger_id="L000001",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_exact_match(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.EXACT_MATCH

    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.amount == ledger.amount
    assert settlement.currency == ledger.currency
    assert settlement.settlement_date == ledger.transaction_date
    assert settlement.reference == ledger.reference

    assert result.ground_truth == {
        "S000001": ["L000001"],
    }


def test_rounding_difference_preserves_ground_truth():
    context = ScenarioContext(
        settlement_id="S000002",
        ledger_id="L000002",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_rounding_difference(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.ROUNDING_DIFFERENCE

    assert settlement.amount != ledger.amount
    assert settlement.amount - ledger.amount == Decimal("0.02")

    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.settlement_date == ledger.transaction_date
    assert settlement.reference == ledger.reference

    assert result.ground_truth == {
        "S000002": ["L000002"],
    }


def test_date_lag_preserves_ground_truth():
    context = ScenarioContext(
        settlement_id="S000003",
        ledger_id="L000003",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_date_lag(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.DATE_LAG

    assert settlement.amount == ledger.amount
    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.reference == ledger.reference

    assert (
        ledger.transaction_date - settlement.settlement_date
        == timedelta(days=2)
    )

    assert result.ground_truth == {
        "S000003": ["L000003"],
    }


def test_missing_reference_preserves_ground_truth():
    context = ScenarioContext(
        settlement_id="S000004",
        ledger_id="L000004",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_missing_reference(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.MISSING_REFERENCE

    assert settlement.reference is None
    assert ledger.reference is None

    assert settlement.amount == ledger.amount
    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.settlement_date == ledger.transaction_date

    assert result.ground_truth == {
        "S000004": ["L000004"],
    }


def test_wrong_merchant_produces_no_match_ground_truth():
    context = ScenarioContext(
        settlement_id="S000005",
        ledger_id="L000005",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_wrong_merchant(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.WRONG_MERCHANT

    assert settlement.merchant_id != ledger.merchant_id

    assert settlement.amount == ledger.amount
    assert settlement.reference == ledger.reference
    assert settlement.settlement_date == ledger.transaction_date

    assert result.ground_truth == {
        "S000005": None,
    }


def test_missing_ledger_produces_no_match_ground_truth():
    context = ScenarioContext(
        settlement_id="S000006",
        ledger_id="L000006",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_missing_ledger(context)

    settlement = result.settlements[0]

    assert result.scenario == Scenario.MISSING_LEDGER

    assert len(result.settlements) == 1
    assert len(result.ledger_records) == 0

    assert settlement.merchant_id.startswith("M")
    assert settlement.amount > 0
    assert settlement.reference is not None

    assert result.ground_truth == {
        "S000006": None,
    }


def test_corrupted_reference_preserves_ground_truth():
    context = ScenarioContext(
        settlement_id="S000007",
        ledger_id="L000007",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_corrupted_reference(context)

    settlement = result.settlements[0]
    ledger = result.ledger_records[0]

    assert result.scenario == Scenario.CORRUPTED_REFERENCE

    assert settlement.amount == ledger.amount
    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.settlement_date == ledger.transaction_date

    assert settlement.reference is not None
    assert ledger.reference is not None
    assert settlement.reference != ledger.reference

    assert settlement.reference.replace("-", "") == ledger.reference

    assert result.ground_truth == {
        "S000007": ["L000007"],
    }


def test_duplicate_creates_multiple_ledger_candidates():
    context = ScenarioContext(
        settlement_id="S000008",
        ledger_id="L000008",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_duplicate(context)

    settlement = result.settlements[0]
    ledger, duplicate_ledger = result.ledger_records

    assert result.scenario == Scenario.DUPLICATE

    assert len(result.settlements) == 1
    assert len(result.ledger_records) == 2

    assert settlement.merchant_id == ledger.merchant_id
    assert settlement.merchant_id == duplicate_ledger.merchant_id

    assert settlement.amount == ledger.amount
    assert settlement.amount == duplicate_ledger.amount

    assert settlement.reference == ledger.reference
    assert settlement.reference == duplicate_ledger.reference

    assert ledger.ledger_id != duplicate_ledger.ledger_id

    assert result.ground_truth == {
        "S000008": ["L000008"],
    }


def test_multiple_candidates_creates_competing_ledger_records():
    context = ScenarioContext(
        settlement_id="S000009",
        ledger_id="L000009",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_multiple_candidates(context)

    settlement = result.settlements[0]

    assert result.scenario == Scenario.MULTIPLE_CANDIDATES

    assert len(result.settlements) == 1
    assert len(result.ledger_records) == 3

    ledger_ids = {
        ledger.ledger_id
        for ledger in result.ledger_records
    }

    assert len(ledger_ids) == 3
    assert context.ledger_id in ledger_ids

    for ledger in result.ledger_records:
        assert ledger.merchant_id == settlement.merchant_id
        assert ledger.amount == settlement.amount
        assert ledger.reference is None

    assert result.ground_truth == {
        "S000009": ["L000009"],
    }

    expected_dates = {
        settlement.settlement_date - timedelta(days=1),
        settlement.settlement_date,
        settlement.settlement_date + timedelta(days=1),
    }

    actual_dates = {
        ledger.transaction_date
        for ledger in result.ledger_records
    }

    assert actual_dates == expected_dates


def test_partial_refund_creates_related_ledger_events():
    context = ScenarioContext(
        settlement_id="S000010",
        ledger_id="L000010",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_partial_refund(context)

    settlement = result.settlements[0]
    payment_ledger, refund_ledger = result.ledger_records

    assert result.scenario == Scenario.PARTIAL_REFUND

    assert len(result.settlements) == 1
    assert len(result.ledger_records) == 2

    assert payment_ledger.entry_type == LedgerEntryType.PAYMENT
    assert refund_ledger.entry_type == LedgerEntryType.REFUND

    assert payment_ledger.amount > refund_ledger.amount
    assert (
        payment_ledger.amount - refund_ledger.amount
        == settlement.amount
    )

    assert payment_ledger.merchant_id == settlement.merchant_id
    assert refund_ledger.merchant_id == settlement.merchant_id

    assert payment_ledger.reference == settlement.reference

    assert refund_ledger.reference is not None
    assert refund_ledger.reference.endswith("-REFUND")

    assert (
        refund_ledger.transaction_date - payment_ledger.transaction_date
        == timedelta(days=1)
    )

    assert result.ground_truth == {
        "S000010": ["L000010", "L000011"],
    }