import asyncio
import json
import os
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from app.db.session import SessionFactory
from app.domain.ai.models import AIResolutionDecision
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
)
from app.infrastructure.llm.ollama_provider import OllamaResolver
from app.repositories.candidate_retriever import CandidateRetriever


load_dotenv()


# -------------------------------------------------------------------
# Benchmark configuration
# -------------------------------------------------------------------

RESULTS_DIR = Path("evaluation/results")

RESULTS_FILE = (
    RESULTS_DIR / "ollama_baseline_results_v3.jsonl"
)

# Local Ollama inference.
# Keep this at 1 for stable local benchmarking.
CONCURRENCY = 1

# Records are grouped into batches for progress reporting.
BATCH_SIZE = 10

# Default full benchmark size.
#
# One-record test:
#   $env:BENCHMARK_LIMIT="1"
#   python -m evaluation.benchmark_llm
#
# Five-record test:
#   $env:BENCHMARK_LIMIT="5"
#
# Remove afterwards:
#   Remove-Item Env:BENCHMARK_LIMIT
BENCHMARK_LIMIT = int(
    os.getenv("BENCHMARK_LIMIT", "400")
)


# -------------------------------------------------------------------
# Result model
# -------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    settlement_id: str

    # Ground truth:
    #   None        -> no matching ledger set
    #   ["L001"]    -> single-ledger match
    #   ["L001", ...] -> multi-ledger match
    expected: list[str] | None

    decision: str | None
    candidate_ids: list[str]

    confidence: float | None

    candidate_count: int

    latency_seconds: float

    input_tokens: int
    output_tokens: int
    total_tokens: int

    error_type: str | None = None
    error_message: str | None = None


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def load_completed_results() -> dict[str, BenchmarkResult]:
    """Load successfully persisted benchmark results."""

    if not RESULTS_FILE.exists():
        return {}

    completed: dict[str, BenchmarkResult] = {}

    with RESULTS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)

                result = BenchmarkResult(
                    **data
                )

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ) as exc:
                print(
                    "Warning: skipping malformed result: "
                    f"{exc}",
                    flush=True,
                )
                continue

            completed[result.settlement_id] = result

    return completed


def persist_result(
    result: BenchmarkResult,
) -> None:
    """Persist one successful benchmark result immediately."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = {
        "settlement_id": result.settlement_id,
        "expected": result.expected,
        "decision": result.decision,
        "candidate_ids": result.candidate_ids,
        "confidence": result.confidence,
        "candidate_count": result.candidate_count,
        "latency_seconds": result.latency_seconds,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "total_tokens": result.total_tokens,
        "error_type": result.error_type,
        "error_message": result.error_message,
    }

    with RESULTS_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )


# -------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------

def load_settlements() -> list[SettlementRecord]:
    from evaluation.benchmark_rules import (
        load_settlements,
    )

    return load_settlements()


def load_ground_truth() -> dict[str, list[str] | None]:
    from evaluation.benchmark_rules import (
        load_ground_truth,
    )

    return load_ground_truth()


# -------------------------------------------------------------------
# ORM -> domain conversion
# -------------------------------------------------------------------

def to_domain_ledger(
    ledger,
) -> LedgerRecord:
    return LedgerRecord(
        ledger_id=ledger.ledger_id,
        merchant_id=ledger.merchant_id,
        amount=ledger.amount,
        currency=ledger.currency,
        transaction_date=ledger.transaction_date,
        reference=ledger.reference,
        entry_type=ledger.entry_type,
    )


# -------------------------------------------------------------------
# Candidate retrieval
# -------------------------------------------------------------------

async def retrieve_candidates(
    session,
    settlement: SettlementRecord,
) -> list[LedgerRecord]:

    retriever = CandidateRetriever(
        session
    )

    orm_candidates = await retriever.retrieve(
        merchant_id=settlement.merchant_id,
        currency=settlement.currency,
        amount=settlement.amount,
        transaction_date=settlement.settlement_date,
        reference=settlement.reference,
        amount_tolerance=Decimal("0.02"),
        date_window_days=2,
        limit=50,
    )

    return [
        to_domain_ledger(ledger)
        for ledger in orm_candidates
    ]


# -------------------------------------------------------------------
# Single LLM resolution
# -------------------------------------------------------------------

async def resolve_one(
    *,
    resolver: OllamaResolver,
    settlement: SettlementRecord,
    candidates: list[LedgerRecord],
    expected: list[str] | None,
    semaphore: asyncio.Semaphore,
) -> BenchmarkResult:

    async with semaphore:

        start = time.perf_counter()

        try:
            result = await resolver.resolve(
                settlement,
                candidates,
            )

            latency = (
                time.perf_counter()
                - start
            )

            return BenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision=(
                    result.resolution.decision.value
                ),
                candidate_ids=list(
                    result.resolution.candidate_ids
                ),
                confidence=(
                    result.resolution.confidence
                ),
                candidate_count=len(
                    candidates
                ),
                latency_seconds=latency,
                input_tokens=(
                    result.usage.input_tokens
                ),
                output_tokens=(
                    result.usage.output_tokens
                ),
                total_tokens=(
                    result.usage.total_tokens
                ),
            )

        except LLMTimeoutError as exc:

            latency = (
                time.perf_counter()
                - start
            )

            cause = exc.__cause__

            return BenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision=None,
                candidate_ids=[],
                confidence=None,
                candidate_count=len(
                    candidates
                ),
                latency_seconds=latency,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                error_type=(
                    type(cause).__name__
                    if cause is not None
                    else type(exc).__name__
                ),
                error_message=(
                    str(cause)
                    if cause is not None
                    else str(exc)
                ),
            )

        except LLMProviderError as exc:

            latency = (
                time.perf_counter()
                - start
            )

            cause = exc.__cause__

            return BenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision=None,
                candidate_ids=[],
                confidence=None,
                candidate_count=len(
                    candidates
                ),
                latency_seconds=latency,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                error_type=(
                    type(cause).__name__
                    if cause is not None
                    else type(exc).__name__
                ),
                error_message=(
                    str(cause)
                    if cause is not None
                    else str(exc)
                ),
            )

        except Exception as exc:

            latency = (
                time.perf_counter()
                - start
            )

            return BenchmarkResult(
                settlement_id=(
                    settlement.settlement_id
                ),
                expected=expected,
                decision=None,
                candidate_ids=[],
                confidence=None,
                candidate_count=len(
                    candidates
                ),
                latency_seconds=latency,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )


# -------------------------------------------------------------------
# Batch execution
# -------------------------------------------------------------------

async def run_batch(
    *,
    resolver: OllamaResolver,
    batch: list[
        tuple[
            SettlementRecord,
            list[LedgerRecord],
            list[str] | None,
        ]
    ],
    semaphore: asyncio.Semaphore,
    completed_before: int,
    total: int,
) -> list[BenchmarkResult]:

    tasks = []

    for settlement, candidates, expected in batch:

        tasks.append(
            resolve_one(
                resolver=resolver,
                settlement=settlement,
                candidates=candidates,
                expected=expected,
                semaphore=semaphore,
            )
        )

    results: list[BenchmarkResult] = []

    for task in asyncio.as_completed(tasks):

        result = await task

        results.append(result)

        # Only successful requests are persisted.
        #
        # Failed requests remain pending so that a later
        # benchmark run can retry them.
        if result.error_type is None:
            persist_result(result)

        completed = (
            completed_before
            + len(results)
        )

        print(
            f"\rCompleted {completed}/{total}",
            end="",
            flush=True,
        )

    return results


# -------------------------------------------------------------------
# Metrics
# -------------------------------------------------------------------

def calculate_metrics(
    results: list[BenchmarkResult],
) -> dict[str, float]:
    """Calculate benchmark metrics.

    A positive case is correct only when the complete predicted
    candidate set exactly matches the ground-truth candidate set.

    This supports both:
        ["L001"]

    and:

        ["L001", "L002"]
    """

    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0

    for result in results:

        predicted_match = (
            result.decision
            == AIResolutionDecision.MATCH.value
            and bool(result.candidate_ids)
        )

        # -----------------------------------------------------------
        # Provider/inference failure
        # -----------------------------------------------------------

        if result.error_type is not None:

            if result.expected is None:
                true_negatives += 1

            else:
                false_negatives += 1

            continue

        # -----------------------------------------------------------
        # Ground truth: NO MATCH
        # -----------------------------------------------------------

        if result.expected is None:

            if predicted_match:
                false_positives += 1

            else:
                true_negatives += 1

            continue

        # -----------------------------------------------------------
        # Ground truth: one or multiple expected candidates
        # -----------------------------------------------------------

        expected_ids = set(
            result.expected
        )

        predicted_ids = set(
            result.candidate_ids
        )

        if (
            result.decision
            == AIResolutionDecision.MATCH.value
            and predicted_ids == expected_ids
        ):
            true_positives += 1

        else:
            false_negatives += 1

    total = len(results)

    return {
        "accuracy": (
            (
                true_positives
                + true_negatives
            )
            / total
            if total
            else 0.0
        ),
        "precision": (
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
        ),
        "recall": (
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
        ),
        "false_match_rate": (
            false_positives / total
            if total
            else 0.0
        ),
    }


# -------------------------------------------------------------------
# Main benchmark
# -------------------------------------------------------------------

async def main() -> None:

    model = os.getenv(
        "OLLAMA_MODEL",
        "qwen2.5:3b",
    )

    all_settlements = load_settlements()
    ground_truth = load_ground_truth()

    settlements = all_settlements[
        :BENCHMARK_LIMIT
    ]

    # ---------------------------------------------------------------
    # Resume persisted successful results
    # ---------------------------------------------------------------

    persisted_results = (
        load_completed_results()
    )

    pending_settlements = [
        settlement
        for settlement in settlements
        if settlement.settlement_id
        not in persisted_results
    ]

    total = len(settlements)

    print(
        f"Starting LLM benchmark: {total} records"
    )

    print(
        "Provider: Ollama"
    )

    print(
        f"Model: {model}"
    )

    print(
        f"Concurrency: {CONCURRENCY}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    print(
        f"Previously completed: "
        f"{len(persisted_results)}"
    )

    print(
        f"Remaining: "
        f"{len(pending_settlements)}"
    )

    print()

    # ---------------------------------------------------------------
    # Candidate retrieval
    # ---------------------------------------------------------------

    candidate_inputs = []

    if pending_settlements:

        print(
            "Retrieving candidates...",
            flush=True,
        )

        async with SessionFactory() as session:

            for settlement in pending_settlements:

                candidates = (
                    await retrieve_candidates(
                        session=session,
                        settlement=settlement,
                    )
                )

                candidate_inputs.append(
                    (
                        settlement,
                        candidates,
                        ground_truth[
                            settlement.settlement_id
                        ],
                    )
                )

        print(
            "Candidate retrieval complete.",
            flush=True,
        )

        candidate_counts = [
            len(candidates)
            for (
                _,
                candidates,
                _,
            ) in candidate_inputs
        ]

        print(
            f"Average candidates: "
            f"{statistics.mean(candidate_counts):.2f}"
        )

        print(
            f"Max candidates: "
            f"{max(candidate_counts)}"
        )

        print()

    else:

        print(
            "No pending records."
        )

    # ---------------------------------------------------------------
    # Ollama resolver
    # ---------------------------------------------------------------

    resolver = OllamaResolver(
        model=model,
        timeout=120.0,
    )

    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )

    benchmark_start = (
        time.perf_counter()
    )

    current_results: list[
        BenchmarkResult
    ] = []

    # ---------------------------------------------------------------
    # Run benchmark
    # ---------------------------------------------------------------

    for start in range(
        0,
        len(candidate_inputs),
        BATCH_SIZE,
    ):

        batch = candidate_inputs[
            start : start + BATCH_SIZE
        ]

        batch_results = await run_batch(
            resolver=resolver,
            batch=batch,
            semaphore=semaphore,
            completed_before=len(
                current_results
            ),
            total=len(
                pending_settlements
            ),
        )

        current_results.extend(
            batch_results
        )

        batch_failures = [
            result
            for result in batch_results
            if result.error_type is not None
        ]

        print()

        print(
            f"Batch completed: "
            f"{len(current_results)}/"
            f"{len(pending_settlements)} "
            f"(failures: "
            f"{len(batch_failures)})"
        )

        for failure in batch_failures[:3]:

            print(
                f"  {failure.settlement_id}: "
                f"{failure.error_type}: "
                f"{failure.error_message}"
            )

    benchmark_elapsed = (
        time.perf_counter()
        - benchmark_start
    )

    # ---------------------------------------------------------------
    # Combine successful persisted + current results
    # ---------------------------------------------------------------

    persisted_results.update(
        {
            result.settlement_id: result
            for result in current_results
            if result.error_type is None
        }
    )

    all_results = [
        persisted_results[
            settlement.settlement_id
        ]
        for settlement in settlements
        if settlement.settlement_id
        in persisted_results
    ]

    # ---------------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------------

    metrics = calculate_metrics(
        all_results
    )

    successful_results = [
        result
        for result in all_results
        if result.error_type is None
    ]

    latencies = [
        result.latency_seconds
        for result in successful_results
    ]

    candidate_counts = [
        result.candidate_count
        for result in all_results
    ]

    total_input_tokens = sum(
        result.input_tokens
        for result in all_results
    )

    total_output_tokens = sum(
        result.output_tokens
        for result in all_results
    )

    total_tokens = sum(
        result.total_tokens
        for result in all_results
    )

    failure_count = (
        total
        - len(successful_results)
    )

    failure_rate = (
        failure_count / total
        if total
        else 0.0
    )

    average_latency = (
        statistics.mean(latencies)
        if latencies
        else 0.0
    )

    p50_latency = (
        statistics.median(latencies)
        if latencies
        else 0.0
    )

    p95_latency = 0.0

    if latencies:

        sorted_latencies = sorted(
            latencies
        )

        # Nearest-rank-style P95.
        p95_position = max(
            1,
            int(
                len(sorted_latencies)
                * 0.95
            ),
        )

        p95_index = min(
            len(sorted_latencies) - 1,
            p95_position - 1,
        )

        p95_latency = (
            sorted_latencies[
                p95_index
            ]
        )

    average_candidates = (
        statistics.mean(
            candidate_counts
        )
        if candidate_counts
        else 0.0
    )

    max_candidates = (
        max(candidate_counts)
        if candidate_counts
        else 0
    )

    decisions = Counter(
        result.decision
        for result in successful_results
    )

    # ---------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------

    print()
    print()

    print(
        "Ollama LLM-only baseline"
    )

    print(
        "------------------------"
    )

    print(
        f"Model              : {model}"
    )

    print(
        f"Records evaluated  : "
        f"{len(all_results)}"
    )

    print(
        f"Successful requests: "
        f"{len(successful_results)}"
    )

    print(
        f"Failures           : "
        f"{failure_count}"
    )

    print(
        f"Accuracy           : "
        f"{metrics['accuracy']:.2%}"
    )

    print(
        f"Precision          : "
        f"{metrics['precision']:.2%}"
    )

    print(
        f"Recall             : "
        f"{metrics['recall']:.2%}"
    )

    print(
        f"False-match rate   : "
        f"{metrics['false_match_rate']:.2%}"
    )

    print(
        f"Failure rate       : "
        f"{failure_rate:.2%}"
    )

    print()

    print(
        "Candidate context"
    )

    print(
        "-----------------"
    )

    print(
        f"Average candidates : "
        f"{average_candidates:.2f}"
    )

    print(
        f"Max candidates     : "
        f"{max_candidates}"
    )

    print()

    print(
        "Latency"
    )

    print(
        "-------"
    )

    print(
        f"Average            : "
        f"{average_latency * 1000:.2f} ms"
    )

    print(
        f"P50                : "
        f"{p50_latency * 1000:.2f} ms"
    )

    print(
        f"P95                : "
        f"{p95_latency * 1000:.2f} ms"
    )

    print()

    print(
        "Usage"
    )

    print(
        "-----"
    )

    print(
        f"Input tokens       : "
        f"{total_input_tokens:,}"
    )

    print(
        f"Output tokens      : "
        f"{total_output_tokens:,}"
    )

    print(
        f"Total tokens       : "
        f"{total_tokens:,}"
    )

    print(
        "API cost           : $0.000000"
    )

    print()

    print(
        "Decisions"
    )

    print(
        "---------"
    )

    for decision, count in sorted(
        decisions.items(),
        key=lambda item: str(
            item[0]
        ),
    ):

        print(
            f"{str(decision):<15}: "
            f"{count}"
        )

    print()

    print(
        f"Total benchmark time : "
        f"{benchmark_elapsed:.2f} sec"
    )

    print(
        f"Results file         : "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())