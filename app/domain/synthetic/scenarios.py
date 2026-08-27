from datetime import date, timedelta
from decimal import Decimal

from app.domain.enums import LedgerEntryType
from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.synthetic.data_factory import SyntheticDataFactory
from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext, ScenarioResult


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
    entry_type: LedgerEntryType = LedgerEntryType.PAYMENT,
) -> LedgerRecord:
    return LedgerRecord(
        ledger_id=ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        currency="INR",
        transaction_date=transaction_date,
        reference=reference,
        entry_type=entry_type,
    )


def _create_factory(context: ScenarioContext) -> SyntheticDataFactory:
    return SyntheticDataFactory(
        rng=context.rng,
        base_date=context.base_date,
    )


def _next_ledger_id(ledger_id: str, offset: int = 1) -> str:
    number = int(ledger_id[1:])
    return f"L{number + offset:06d}"


def generate_exact_match(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()
    reference = factory.reference(context.settlement_id)

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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_rounding_difference(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    settlement_amount = factory.amount()
    ledger_amount = settlement_amount - Decimal("0.02")
    settlement_date = factory.transaction_date()
    reference = factory.reference(context.settlement_id)

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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_date_lag(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()
    ledger_date = settlement_date + timedelta(days=2)
    reference = factory.reference(context.settlement_id)

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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_missing_reference(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()

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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_wrong_merchant(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    settlement_merchant_id = factory.merchant_id()
    ledger_merchant_id = factory.merchant_id()

    while ledger_merchant_id == settlement_merchant_id:
        ledger_merchant_id = factory.merchant_id()

    amount = factory.amount()
    settlement_date = factory.transaction_date()
    reference = factory.reference(context.settlement_id)

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
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()
    reference = factory.reference(context.settlement_id)

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
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()

    settlement_reference = factory.reference(context.settlement_id)
    corrupted_reference = settlement_reference.replace("-", "")

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
        reference=corrupted_reference,
    )

    return ScenarioResult(
        scenario=Scenario.CORRUPTED_REFERENCE,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_duplicate(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    transaction_date = factory.transaction_date()
    reference = factory.reference(context.settlement_id)

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

    duplicate_ledger = create_ledger(
        ledger_id=_next_ledger_id(context.ledger_id),
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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_multiple_candidates(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()
    amount = factory.amount()
    settlement_date = factory.transaction_date()

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
        ledger_id=_next_ledger_id(context.ledger_id, 1),
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=settlement_date - timedelta(days=1),
        reference=None,
    )

    next_ledger = create_ledger(
        ledger_id=_next_ledger_id(context.ledger_id, 2),
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
            context.settlement_id: [context.ledger_id],
        },
    )


def generate_partial_refund(
    context: ScenarioContext,
) -> ScenarioResult:
    factory = _create_factory(context)

    merchant_id = factory.merchant_id()

    original_amount = factory.amount()

    # Keep the refund smaller than the original payment.
    max_refund_cents = int(original_amount * 100) - 1
    refund_cents = factory.rng.randint(
        1,
        min(max_refund_cents, 10_000),
    )
    refund_amount = Decimal(refund_cents) / Decimal("100")

    settlement_amount = original_amount - refund_amount
    settlement_date = factory.transaction_date()

    settlement_reference = factory.reference(context.settlement_id)
    refund_reference = f"{settlement_reference}-REFUND"

    settlement = create_settlement(
        settlement_id=context.settlement_id,
        merchant_id=merchant_id,
        amount=settlement_amount,
        settlement_date=settlement_date,
        reference=settlement_reference,
    )

    payment_ledger = create_ledger(
        ledger_id=context.ledger_id,
        merchant_id=merchant_id,
        amount=original_amount,
        transaction_date=settlement_date,
        reference=settlement_reference,
        entry_type=LedgerEntryType.PAYMENT,
    )

    refund_ledger_id = _next_ledger_id(context.ledger_id)

    refund_ledger = create_ledger(
        ledger_id=refund_ledger_id,
        merchant_id=merchant_id,
        amount=refund_amount,
        transaction_date=settlement_date + timedelta(days=1),
        reference=refund_reference,
        entry_type=LedgerEntryType.REFUND,
    )

    return ScenarioResult(
        scenario=Scenario.PARTIAL_REFUND,
        settlements=[settlement],
        ledger_records=[
            payment_ledger,
            refund_ledger,
        ],
        ground_truth={
            context.settlement_id: [
                context.ledger_id,
                refund_ledger_id,
            ],
        },
    )