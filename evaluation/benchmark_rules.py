import csv
import json
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.domain.enums import LedgerEntryType, MatchStatus
from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.reconciliation.rule_matcher import RuleMatcher


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

DATA_DIR = Path("data")

RESULTS_DIR = Path(
    "evaluation/results"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "rules_baseline_results_v1.jsonl"
)


# -------------------------------------------------------------------
# Result model
# -------------------------------------------------------------------

@dataclass
class RulesBenchmarkResult:
    settlement_id: str
    expected: list[str] | None

    decision: str
    candidate_ids: list[str]

    confidence: float
    evidence_codes: list[str]
    source: str

    correct: bool
    automated: bool

    latency_seconds: float

    error_type: str | None = None
    error_message: str | None = None


# -------------------------------------------------------------------
# Dataset loading
# -------------------------------------------------------------------

def load_settlements() -> list[SettlementRecord]:
    records: list[SettlementRecord] = []

    with (
        DATA_DIR / "settlements.csv"
    ).open(
        newline="",
        encoding="utf-8",
    ) as file:

        for row in csv.DictReader(file):
            records.append(
                SettlementRecord(
                    settlement_id=row["settlement_id"],
                    merchant_id=row["merchant_id"],
                    amount=Decimal(
                        row["amount"]
                    ),
                    currency=row["currency"],
                    settlement_date=date.fromisoformat(
                        row["settlement_date"]
                    ),
                    reference=(
                        row["reference"]
                        or None
                    ),
                )
            )

    return records


def load_ledgers() -> list[LedgerRecord]:
    records: list[LedgerRecord] = []

    with (
        DATA_DIR / "ledger.csv"
    ).open(
        newline="",
        encoding="utf-8",
    ) as file:

        for row in csv.DictReader(file):
            records.append(
                LedgerRecord(
                    ledger_id=row["ledger_id"],
                    merchant_id=row["merchant_id"],
                    amount=Decimal(
                        row["amount"]
                    ),
                    currency=row["currency"],
                    transaction_date=date.fromisoformat(
                        row["transaction_date"]
                    ),
                    reference=(
                        row["reference"]
                        or None
                    ),
                    entry_type=LedgerEntryType(
                        row["entry_type"]
                    ),
                )
            )

    return records


def load_ground_truth() -> dict[
    str,
    list[str] | None,
]:
    with (
        DATA_DIR / "ground_truth.json"
    ).open(
        encoding="utf-8",
    ) as file:
        return json.load(file)


# -------------------------------------------------------------------
# Candidate construction
# -------------------------------------------------------------------

def build_candidates(
    settlement: SettlementRecord,
    ledgers: list[LedgerRecord],
) -> list[LedgerRecord]:
    """
    Day-3 in-memory candidate universe.

    This intentionally remains independent from the production
    PostgreSQL candidate retriever so this benchmark continues to
    measure the deterministic rule matcher itself.
    """

    return [
        ledger
        for ledger in ledgers
        if ledger.currency
        == settlement.currency
    ]


# -------------------------------------------------------------------
# Correctness
# -------------------------------------------------------------------

def candidate_sets_equal(
    actual: list[str],
    expected: list[str] | None,
) -> bool:
    """
    Candidate ordering is irrelevant.

    For a positive ground truth:
        exact candidate-set equality is required.

    For negative ground truth:
        there must be no predicted candidates.
    """

    if expected is None:
        return not actual

    return set(actual) == set(expected)


def get_candidate_ids(
    decision,
) -> list[str]:
    """
    Support both the current multi-candidate MatchDecision and older
    single-ledger compatibility.

    Current domain model:
        decision.candidate_ids

    Legacy domain model:
        decision.ledger_id
    """

    candidate_ids = getattr(
        decision,
        "candidate_ids",
        None,
    )

    if candidate_ids is not None:
        return list(candidate_ids)

    ledger_id = getattr(
        decision,
        "ledger_id",
        None,
    )

    if ledger_id is None:
        return []

    return [ledger_id]


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def persist_result(
    result: RulesBenchmarkResult,
) -> None:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RESULTS_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                asdict(result),
                ensure_ascii=False,
            )
            + "\n"
        )


# -------------------------------------------------------------------
# Benchmark
# -------------------------------------------------------------------

def main() -> None:
    settlements = load_settlements()
    ledgers = load_ledgers()
    ground_truth = load_ground_truth()

    matcher = RuleMatcher()

    decision_statuses = Counter()
    decision_sources = Counter()

    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0

    matched = 0
    exceptions = 0
    failures = 0

    start = time.perf_counter()

    # ---------------------------------------------------------------
    # Fresh deterministic benchmark file.
    #
    # Rules execution is cheap, so unlike the LLM benchmark we simply
    # rebuild the complete record-level result file every time.
    # ---------------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTS_FILE.write_text(
        "",
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Evaluate each settlement independently.
    # ---------------------------------------------------------------

    for settlement in settlements:
        record_start = time.perf_counter()

        expected = ground_truth[
            settlement.settlement_id
        ]

        try:
            candidates = build_candidates(
                settlement,
                ledgers,
            )

            decision = matcher.match(
                settlement,
                candidates,
            )

            candidate_ids = get_candidate_ids(
                decision
            )

            decision_status = (
                decision.status.value
            )

            evidence_codes = list(
                getattr(
                    decision,
                    "evidence",
                    [],
                )
            )

            source = str(
                getattr(
                    decision,
                    "source",
                    "rule_matcher",
                )
            )

            confidence = float(
                getattr(
                    decision,
                    "confidence",
                    0.0,
                )
            )

            correct = candidate_sets_equal(
                candidate_ids,
                expected,
            )

            automated = (
                decision.status
                == MatchStatus.MATCHED_RULE
            )

            latency = (
                time.perf_counter()
                - record_start
            )

            result = RulesBenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision=decision_status,
                candidate_ids=candidate_ids,
                confidence=confidence,
                evidence_codes=evidence_codes,
                source=source,
                correct=correct,
                automated=automated,
                latency_seconds=latency,
            )

            persist_result(result)

            decision_statuses[
                decision_status
            ] += 1

            decision_sources[
                source
            ] += 1

            if correct:
                if expected is None:
                    true_negatives += 1
                else:
                    true_positives += 1

            else:
                if expected is None:
                    false_positives += 1
                else:
                    false_negatives += 1

            if automated:
                matched += 1

            if decision.status in {
                MatchStatus.HUMAN_REVIEW,
                MatchStatus.NO_MATCH,
            }:
                exceptions += 1

        except Exception as exc:
            latency = (
                time.perf_counter()
                - record_start
            )

            failures += 1

            result = RulesBenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision="ERROR",
                candidate_ids=[],
                confidence=0.0,
                evidence_codes=[],
                source="rule_benchmark",
                correct=False,
                automated=False,
                latency_seconds=latency,
                error_type=type(
                    exc
                ).__name__,
                error_message=str(exc),
            )

            persist_result(result)

    elapsed = (
        time.perf_counter()
        - start
    )

    total = len(settlements)

    successful = (
        total - failures
    )

    # ---------------------------------------------------------------
    # Aggregate metrics
    # ---------------------------------------------------------------

    accuracy = (
        (true_positives + true_negatives)
        / successful
        if successful
        else 0.0
    )

    precision = (
        true_positives
        / (
            true_positives
            + false_positives
        )
        if (
            true_positives
            + false_positives
        )
        else 0.0
    )

    recall = (
        true_positives
        / (
            true_positives
            + false_negatives
        )
        if (
            true_positives
            + false_negatives
        )
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

    failure_rate = (
        failures / total
        if total
        else 0.0
    )

    throughput = (
        total / elapsed
        if elapsed
        else 0.0
    )

    # ---------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------

    print()
    print(
        "Rules-only baseline"
    )
    print(
        "-------------------"
    )

    print(
        f"Records evaluated : "
        f"{total}"
    )

    print(
        f"Successful        : "
        f"{successful}"
    )

    print(
        f"Failures          : "
        f"{failures}"
    )

    print(
        f"Matched           : "
        f"{matched}"
    )

    print(
        f"Exceptions        : "
        f"{exceptions}"
    )

    print(
        f"Accuracy           : "
        f"{accuracy:.2%}"
    )

    print(
        f"Precision          : "
        f"{precision:.2%}"
    )

    print(
        f"Recall             : "
        f"{recall:.2%}"
    )

    print(
        f"False-match rate   : "
        f"{false_match_rate:.2%}"
    )

    print(
        f"Exception rate     : "
        f"{exception_rate:.2%}"
    )

    print(
        f"Automation rate    : "
        f"{automation_rate:.2%}"
    )

    print(
        f"Failure rate       : "
        f"{failure_rate:.2%}"
    )

    print(
        f"Throughput         : "
        f"{throughput:,.2f} records/sec"
    )

    print(
        f"Elapsed            : "
        f"{elapsed:.4f} sec"
    )

    print()

    print(
        "Decision breakdown"
    )
    print(
        "------------------"
    )

    for status, count in sorted(
        decision_statuses.items()
    ):
        print(
            f"{status:<20}: "
            f"{count}"
        )

    print()

    print(
        "Rule source breakdown"
    )
    print(
        "---------------------"
    )

    for source, count in sorted(
        decision_sources.items()
    ):
        print(
            f"{source:<40}: "
            f"{count}"
        )

    print()

    print(
        f"Results file      : "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()

