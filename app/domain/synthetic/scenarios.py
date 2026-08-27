from datetime import date, timedelta
from decimal import Decimal

from app.domain.synthetic.models import ScenarioContext, ScenarioResult
from app.domain.synthetic.enums import Scenario

from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioResult


def create_settlement(
    settlement_id: str,
    merchant_id: str,
    amount: Decimal,
    settlement_date: date,
    reference: str | None,
) -> SettlementRecord:
    return SettlementRecord(
        settlement_id=settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        currency="INR",
        settlement_date=settlement_date,
        reference=reference,
    )


def create_ledger(
    ledger_id: str,
    merchant_id: str,
    amount: Decimal,
    transaction_date: date,
    reference: str | None,
) -> LedgerRecord:
    return LedgerRecord(
        ledger_id=ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        currency="INR",
        transaction_date=transaction_date,
        reference=reference,
    )

def generate_exact_match(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date
    reference = "UTR100001"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.EXACT_MATCH,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )

def generate_rounding_difference(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    settlement_amount = Decimal("1000.00")
    ledger_amount = Decimal("999.98")
    settlement_date = context.base_date
    reference = "UTR100002"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=settlement_amount,
        settlement_date=settlement_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=ledger_amount,
        transaction_date=settlement_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.ROUNDING_DIFFERENCE,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )

def generate_date_lag(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date
    ledger_date = settlement_date + timedelta(days=2)
    reference = "UTR100003"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=ledger_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.DATE_LAG,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )


def generate_missing_reference(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=None,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date,
        reference=None,
    )

    return ScenarioResult(
        scenario=Scenario.MISSING_REFERENCE,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )

def generate_wrong_merchant(
    context: ScenarioContext,
) -> ScenarioResult:
    settlement_merchant_id = "M001"
    ledger_merchant_id = "M002"

    amount = Decimal("1000.00")
    settlement_date = context.base_date
    reference = "UTR100005"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=settlement_merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=ledger_merchant_id,
        amount=amount,
        transaction_date=settlement_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.WRONG_MERCHANT,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: None,
        },
    )


def generate_missing_ledger(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date
    reference = "UTR100006"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.MISSING_LEDGER,
        settlements=[settlement],
        ledger_records=[],
        ground_truth={
            context.settlement_id: None,
        },
    )

def generate_corrupted_reference(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date

    settlement_reference = "UTR100007"
    ledger_reference = "UTR-100007"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=settlement_reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date,
        reference=ledger_reference,
    )

    return ScenarioResult(
        scenario=Scenario.CORRUPTED_REFERENCE,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )

def generate_duplicate(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    transaction_date = context.base_date
    reference = "UTR100008"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=transaction_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=transaction_date,
        reference=reference,
    )

    duplicate_ledger_id = f"L{int(context.ledger_id[1:]) + 1:06d}"

    duplicate_ledger = create_ledger(
        ledger_id=duplicate_ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=transaction_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.DUPLICATE,
        settlements=[settlement],
        ledger_records=[ledger, duplicate_ledger],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )

def generate_multiple_candidates(
    context: ScenarioContext,
) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    settlement_date = context.base_date

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        settlement_date=settlement_date,
        reference=None,
    )

    true_ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date,
        reference=None,
    )

    previous_ledger = create_ledger(
        ledger_id=f"L{int(context.ledger_id[1:]) + 1:06d}",
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date - timedelta(days=1),
        reference=None,
    )

    next_ledger = create_ledger(
        ledger_id=f"L{int(context.ledger_id[1:]) + 2:06d}",
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date + timedelta(days=1),
        reference=None,
    )

    return ScenarioResult(
        scenario=Scenario.MULTIPLE_CANDIDATES,
        settlements=[settlement],
        ledger_records=[
            previous_ledger,
            true_ledger,
            next_ledger,
        ],
        ground_truth={
            context.settlement_id: context.ledger_id,
        },
    )