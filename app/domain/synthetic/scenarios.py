from datetime import date
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