from app.domain.synthetic.models import GeneratedDataset
from app.domain.synthetic.enums import Scenario
from app.domain.models import LedgerEntryType

from app.domain.synthetic.distribution import DEFAULT_DISTRIBUTION


class DatasetValidationError(ValueError):
    pass


def validate_dataset(dataset: GeneratedDataset) -> None:
    settlement_ids = [
    settlement.settlement_id
    for settlement in dataset.settlements
    ]

    ledger_ids = [
    ledger.ledger_id
    for ledger in dataset.ledger_records
    ]

    if len(settlement_ids) != len(set(settlement_ids)):
        raise DatasetValidationError(
        "Settlement IDs must be unique."
    )

    if len(ledger_ids) != len(set(ledger_ids)):
        raise DatasetValidationError(
        "Ledger IDs must be unique."
    )

    if len(settlement_ids) != len(dataset.ground_truth):
        raise DatasetValidationError(
        "Every settlement must have exactly one ground-truth entry."
    )

    if set(settlement_ids) != set(dataset.scenario_by_settlement):
        raise DatasetValidationError(
        "Every settlement must have scenario metadata."
    )

    all_ledger_ids = set(ledger_ids)

    for settlement_id, truth_ledger_ids in dataset.ground_truth.items():
        if truth_ledger_ids is None:
            continue

        for ledger_id in truth_ledger_ids:
            if ledger_id not in all_ledger_ids:
                raise DatasetValidationError(
                f"{settlement_id} references missing ledger "
                f"record {ledger_id}."
            )

    actual_counts = {}

    for scenario in dataset.scenario_by_settlement.values():
        actual_counts[scenario] = actual_counts.get(scenario, 0) + 1

    if actual_counts != DEFAULT_DISTRIBUTION.counts:
        raise DatasetValidationError(
        "Generated scenario distribution does not match "
        "the expected distribution."
    )

    for settlement in dataset.settlements:
        scenario = dataset.scenario_by_settlement[
        settlement.settlement_id
    ]

        if scenario != Scenario.PARTIAL_REFUND:
            continue

        truth_ids = dataset.ground_truth[settlement.settlement_id]

        if truth_ids is None or len(truth_ids) != 2:
            raise DatasetValidationError(
            f"Partial refund {settlement.settlement_id} "
            "must reference exactly two ledger records."
        )

        ledger_by_id = {
        ledger.ledger_id: ledger
        for ledger in dataset.ledger_records
        }

        payment = ledger_by_id[truth_ids[0]]
        refund = ledger_by_id[truth_ids[1]]

        if payment.entry_type != LedgerEntryType.PAYMENT:
            raise DatasetValidationError(
            f"Partial refund {settlement.settlement_id} "
            "must reference a PAYMENT entry first."
        )

        if refund.entry_type != LedgerEntryType.REFUND:
            raise DatasetValidationError(
            f"Partial refund {settlement.settlement_id} "
            "must reference a REFUND entry second."
        )

        if payment.amount - refund.amount != settlement.amount:
            raise DatasetValidationError(
            f"Partial refund {settlement.settlement_id} "
            "does not reconcile to the settlement amount."
        )