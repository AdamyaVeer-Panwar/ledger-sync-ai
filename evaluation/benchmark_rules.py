import csv
import json
import time
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.domain.enums import LedgerEntryType, MatchStatus
from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.reconciliation.rule_matcher import RuleMatcher


DATA_DIR = Path("data")


def load_settlements() -> list[SettlementRecord]:
    records: list[SettlementRecord] = []

    with open(
        DATA_DIR / "settlements.csv",
        newline="",
        encoding="utf-8",
    ) as file:
        for row in csv.DictReader(file):
            records.append(
                SettlementRecord(
                    settlement_id=row["settlement_id"],
                    merchant_id=row["merchant_id"],
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    settlement_date=date.fromisoformat(
                        row["settlement_date"]
                    ),
                    reference=row["reference"] or None,
                )
            )

    return records


def load_ledgers() -> list[LedgerRecord]:
    records: list[LedgerRecord] = []

    with open(
        DATA_DIR / "ledger.csv",
        newline="",
        encoding="utf-8",
    ) as file:
        for row in csv.DictReader(file):
            records.append(
                LedgerRecord(
                    ledger_id=row["ledger_id"],
                    merchant_id=row["merchant_id"],
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    transaction_date=date.fromisoformat(
                        row["transaction_date"]
                    ),
                    reference=row["reference"] or None,
                    entry_type=LedgerEntryType(
                        row["entry_type"]
                    ),
                )
            )

    return records


def load_ground_truth() -> dict[str, list[str] | None]:
    with open(
        DATA_DIR / "ground_truth.json",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_candidates(
    settlement: SettlementRecord,
    ledgers: list[LedgerRecord],
) -> list[LedgerRecord]:
    """Day-3 evaluation candidate universe.

    This intentionally uses a simple in-memory filter.
    Day 4 replaces this with indexed PostgreSQL retrieval.
    """

    return [
        ledger
        for ledger in ledgers
        if ledger.currency == settlement.currency
    ]


def main() -> None:
    settlements = load_settlements()
    ledgers = load_ledgers()
    ground_truth = load_ground_truth()

    matcher = RuleMatcher()

    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0

    matched = 0
    exceptions = 0

    decision_statuses = Counter()
    decision_sources = Counter()

    start = time.perf_counter()

    for settlement in settlements:
        candidates = build_candidates(
            settlement,
            ledgers,
        )

        decision = matcher.match(
            settlement,
            candidates,
        )

        decision_statuses[decision.status.value] += 1
        decision_sources[decision.source] += 1

        expected = ground_truth[settlement.settlement_id]

        predicted_ledger_id = (
            decision.ledger_id
            if decision.status == MatchStatus.MATCHED_RULE
            else None
        )

        # Current MatchDecision can represent only one ledger_id.
        # Therefore only a single-ledger ground truth can be counted
        # as a complete deterministic match.
        expected_single_match = (
            expected is not None
            and len(expected) == 1
        )

        if expected is None:
            if predicted_ledger_id is None:
                true_negatives += 1
            else:
                false_positives += 1

        elif expected_single_match:
            expected_ledger_id = expected[0]

            if predicted_ledger_id == expected_ledger_id:
                true_positives += 1
                matched += 1
            else:
                false_negatives += 1

        else:
            # Example: PARTIAL_REFUND where ground truth contains
            # multiple ledger IDs but MatchDecision supports only one.
            false_negatives += 1

        if decision.status in {
            MatchStatus.HUMAN_REVIEW,
            MatchStatus.NO_MATCH,
        }:
            exceptions += 1

    elapsed = time.perf_counter() - start
    total = len(settlements)

    accuracy = (
        (true_positives + true_negatives) / total
        if total
        else 0.0
    )

    precision = (
        true_positives
        / (true_positives + false_positives)
        if (true_positives + false_positives)
        else 0.0
    )

    recall = (
        true_positives
        / (true_positives + false_negatives)
        if (true_positives + false_negatives)
        else 0.0
    )

    false_match_rate = (
        false_positives / total
        if total
        else 0.0
    )

    exception_rate = (
        exceptions / total
        if total
        else 0.0
    )

    automation_rate = (
        matched / total
        if total
        else 0.0
    )

    throughput = (
        total / elapsed
        if elapsed
        else 0.0
    )

    print()
    print("Rules-only baseline")
    print("-------------------")
    print(f"Records evaluated : {total}")
    print(f"Matched            : {matched}")
    print(f"Exceptions         : {exceptions}")
    print(f"Accuracy           : {accuracy:.2%}")
    print(f"Precision          : {precision:.2%}")
    print(f"Recall             : {recall:.2%}")
    print(f"False-match rate   : {false_match_rate:.2%}")
    print(f"Exception rate     : {exception_rate:.2%}")
    print(f"Automation rate    : {automation_rate:.2%}")
    print(f"Throughput         : {throughput:,.2f} records/sec")
    print(f"Elapsed            : {elapsed:.4f} sec")

    print()
    print("Decision breakdown")
    print("------------------")

    for status, count in sorted(decision_statuses.items()):
        print(f"{status:<20}: {count}")

    print()
    print("Rule source breakdown")
    print("---------------------")

    for source, count in sorted(decision_sources.items()):
        print(f"{source:<40}: {count}")


if __name__ == "__main__":
    main()