import csv
import json
from pathlib import Path

from app.domain.synthetic.models import GeneratedDataset


def write_dataset(
    dataset: GeneratedDataset,
    output_dir: str | Path,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    _write_settlements(
        dataset,
        output_path / "settlements.csv",
    )

    _write_ledger_records(
        dataset,
        output_path / "ledger.csv",
    )

    _write_ground_truth(
        dataset,
        output_path / "ground_truth.json",
    )

    _write_scenario_manifest(
        dataset,
        output_path / "scenario_manifest.json",
    )


def _write_settlements(
    dataset: GeneratedDataset,
    output_file: Path,
) -> None:
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "settlement_id",
                "merchant_id",
                "amount",
                "currency",
                "settlement_date",
                "reference",
            ]
        )

        for settlement in dataset.settlements:
            writer.writerow(
                [
                    settlement.settlement_id,
                    settlement.merchant_id,
                    str(settlement.amount),
                    settlement.currency,
                    settlement.settlement_date.isoformat(),
                    settlement.reference or "",
                ]
            )


def _write_ledger_records(
    dataset: GeneratedDataset,
    output_file: Path,
) -> None:
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "ledger_id",
                "merchant_id",
                "amount",
                "currency",
                "transaction_date",
                "reference",
                "entry_type",
            ]
        )

        for ledger in dataset.ledger_records:
            writer.writerow(
                [
                    ledger.ledger_id,
                    ledger.merchant_id,
                    str(ledger.amount),
                    ledger.currency,
                    ledger.transaction_date.isoformat(),
                    ledger.reference or "",
                    ledger.entry_type.value,
                ]
            )


def _write_ground_truth(
    dataset: GeneratedDataset,
    output_file: Path,
) -> None:
    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            dataset.ground_truth,
            file,
            indent=2,
            sort_keys=True,
        )


def _write_scenario_manifest(
    dataset: GeneratedDataset,
    output_file: Path,
) -> None:
    """
    Persist scenario provenance separately from the financial data.

    This manifest is evaluation metadata only. It is not consumed by
    the reconciliation engine itself.
    """

    scenario_manifest = {
        settlement_id: scenario.value
        for settlement_id, scenario
        in dataset.scenario_by_settlement.items()
    }

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            scenario_manifest,
            file,
            indent=2,
            sort_keys=True,
        )

