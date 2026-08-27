import json
from datetime import date
from decimal import Decimal

from app.domain.enums import LedgerEntryType
from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import GeneratedDataset
from app.domain.synthetic.serialization import write_dataset
import csv

def test_write_dataset_creates_expected_files(tmp_path):
    dataset = GeneratedDataset(
        settlements=[
            SettlementRecord(
                settlement_id="S000001",
                merchant_id="M001",
                amount=Decimal("900.00"),
                currency="INR",
                settlement_date=date(2026, 8, 25),
                reference="UTR001",
            )
        ],
        ledger_records=[
            LedgerRecord(
                ledger_id="L000001",
                merchant_id="M001",
                amount=Decimal("1000.00"),
                currency="INR",
                transaction_date=date(2026, 8, 25),
                reference="UTR001",
                entry_type=LedgerEntryType.PAYMENT,
            ),
            LedgerRecord(
                ledger_id="L000002",
                merchant_id="M001",
                amount=Decimal("100.00"),
                currency="INR",
                transaction_date=date(2026, 8, 26),
                reference="UTR001-REFUND",
                entry_type=LedgerEntryType.REFUND,
            ),
        ],
        ground_truth={
            "S000001": ["L000001", "L000002"],
        },
        scenario_by_settlement={
            "S000001": Scenario.PARTIAL_REFUND,
        },
    )

    write_dataset(dataset, tmp_path)

    assert (tmp_path / "settlements.csv").exists()
    assert (tmp_path / "ledger.csv").exists()
    assert (tmp_path / "ground_truth.json").exists()

    with (tmp_path / "settlements.csv").open(
        newline="",
        encoding="utf-8",
    ) as file:
        settlements = list(csv.DictReader(file))

    assert settlements == [
        {
            "settlement_id": "S000001",
            "merchant_id": "M001",
            "amount": "900.00",
            "currency": "INR",
            "settlement_date": "2026-08-25",
            "reference": "UTR001",
        }
    ]

    with (tmp_path / "ledger.csv").open(
        newline="",
        encoding="utf-8",
    ) as file:
        ledger_records = list(csv.DictReader(file))

    assert ledger_records == [
        {
            "ledger_id": "L000001",
            "merchant_id": "M001",
            "amount": "1000.00",
            "currency": "INR",
            "transaction_date": "2026-08-25",
            "reference": "UTR001",
            "entry_type": "PAYMENT",
        },
        {
            "ledger_id": "L000002",
            "merchant_id": "M001",
            "amount": "100.00",
            "currency": "INR",
            "transaction_date": "2026-08-26",
            "reference": "UTR001-REFUND",
            "entry_type": "REFUND",
        },
    ]

    with (tmp_path / "ground_truth.json").open(
        encoding="utf-8",
    ) as file:
        ground_truth = json.load(file)

    assert ground_truth == {
        "S000001": ["L000001", "L000002"],
    }