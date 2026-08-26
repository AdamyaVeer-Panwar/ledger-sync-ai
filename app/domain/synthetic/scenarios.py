from datetime import date
from decimal import Decimal

from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioResult


def create_settlement(
    settlement_id: str,
    merchant_id: str,
    amount: Decimal,
    transaction_date: date,
    reference: str | None,
) -> SettlementRecord:
    return SettlementRecord(
        settlement_id=settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        currency="INR",
        settlement_date=transaction_date,
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
    settlement_id: str,
    ledger_id: str,
        ) -> ScenarioResult:
    merchant_id = "M001"
    amount = Decimal("1000.00")
    transaction_date = date(2026, 8, 25)
    reference = "UTR100001"

    settlement = create_settlement(
        settlement_id=settlement_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=transaction_date,
        reference=reference,
    )

    ledger = create_ledger(
        ledger_id=ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        transaction_date=transaction_date,
        reference=reference,
    )

    return ScenarioResult(
        scenario=Scenario.EXACT_MATCH,
        settlements=[settlement],
        ledger_records=[ledger],
        ground_truth={
            settlement_id: ledger_id,
        },
    )