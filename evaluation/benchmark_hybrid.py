import asyncio
import json
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

from app.db.session import SessionFactory
from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusion,
)
from app.domain.reconciliation.hybrid_resolver import (
    HybridResolver,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerifier,
)
from app.domain.reconciliation.policy import (
    PolicyAction,
    PolicyEngine,
)
from app.domain.reconciliation.rule_matcher import (
    RuleMatcher,
)
from app.infrastructure.llm.ollama_provider import (
    OllamaResolver,
)
from app.repositories.candidate_retriever import (
    CandidateRetriever,
)
from evaluation.benchmark_llm import (
    load_ground_truth,
    load_settlements,
)


# -------------------------------------------------------------------
# Benchmark configuration
# -------------------------------------------------------------------

RESULTS_DIR = Path("evaluation/results")

# Historical baseline. Kept for comparison only.
RESULTS_V1_RESULTS_FILE = (
    RESULTS_DIR / "hybrid_baseline_results_v1.jsonl"
)

# Current benchmark output.
RESULTS_FILE = (
    RESULTS_DIR / "hybrid_baseline_results_v2.jsonl"
)

BENCHMARK_LIMIT = int(
    os.getenv("BENCHMARK_LIMIT", "400")
)

MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b",
)

TIMEOUT = float(
    os.getenv("OLLAMA_TIMEOUT", "120.0")
)

BENCHMARK_FRESH = (
    os.getenv("BENCHMARK_FRESH", "0") == "1"
)


# -------------------------------------------------------------------
# Result model
# -------------------------------------------------------------------

@dataclass
class HybridBenchmarkResult:
    settlement_id: str
    expected: list[str] | None

    action: str | None
    candidate_ids: list[str]

    confidence: float | None
    evidence_codes: list[str]
    reason: str | None

    # Explicit observability field.
    #
    # True:
    #     HybridResolver actually entered the LLM path.
    #
    # False:
    #     HybridResolver completed deterministically and did not
    #     invoke the LLM.
    llm_invoked: bool

    latency_seconds: float

    error_type: str | None = None
    error_message: str | None = None


# -------------------------------------------------------------------
# Persistence
# -------------------------------------------------------------------

def load_completed_results() -> dict[
    str,
    HybridBenchmarkResult,
]:
    """
    Load previously successful v2 benchmark results.

    Failed requests are not persisted, so they can be retried on
    a subsequent benchmark run.
    """

    if not RESULTS_FILE.exists():
        return {}

    completed: dict[
        str,
        HybridBenchmarkResult,
    ] = {}

    with RESULTS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)

                result = HybridBenchmarkResult(
                    **data
                )

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ) as exc:
                print(
                    "Warning: skipping malformed "
                    f"Hybrid result at line {line_number}: "
                    f"{exc}",
                    flush=True,
                )
                continue

            completed[result.settlement_id] = result

    return completed


def persist_result(
    result: HybridBenchmarkResult,
) -> None:
    """
    Persist one successful Hybrid benchmark result.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = {
        "settlement_id": result.settlement_id,
        "expected": result.expected,
        "action": result.action,
        "candidate_ids": result.candidate_ids,
        "confidence": result.confidence,
        "evidence_codes": result.evidence_codes,
        "reason": result.reason,
        "llm_invoked": result.llm_invoked,
        "latency_seconds": result.latency_seconds,
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
# Correctness
# -------------------------------------------------------------------

def sets_equal(
    actual: list[str],
    expected: list[str],
) -> bool:
    """
    Candidate ordering should not affect reconciliation correctness.
    """

    return set(actual) == set(expected)


def resolution_is_correct(
    result: HybridBenchmarkResult,
) -> bool:
    """
    Measure whether Hybrid produced the correct reconciliation
    candidate set.

    Positive ground truth:
        candidate_ids must exactly equal expected IDs.

    Negative ground truth:
        action must be NO_MATCH and candidate_ids must be empty.
    """

    if result.error_type is not None:
        return False

    if result.expected is None:
        return (
            result.action
            == PolicyAction.NO_MATCH.value
            and not result.candidate_ids
        )

    return sets_equal(
        result.candidate_ids,
        result.expected,
    )


def is_auto_match(
    result: HybridBenchmarkResult,
) -> bool:
    return (
        result.error_type is None
        and result.action
        == PolicyAction.AUTO_MATCH.value
        and bool(result.candidate_ids)
    )


def auto_match_is_correct(
    result: HybridBenchmarkResult,
) -> bool:
    if not is_auto_match(result):
        return False

    if result.expected is None:
        return False

    return sets_equal(
        result.candidate_ids,
        result.expected,
    )


# -------------------------------------------------------------------
# Single record
# -------------------------------------------------------------------

async def resolve_one(
    *,
    settlement,
    expected: list[str] | None,
) -> HybridBenchmarkResult:

    start = time.perf_counter()

    try:
        async with SessionFactory() as session:
            candidate_retriever = CandidateRetriever(
                session
            )

            resolver = HybridResolver(
                rule_matcher=RuleMatcher(),
                candidate_retriever=candidate_retriever,
                llm_resolver=OllamaResolver(
                    model=MODEL,
                    timeout=TIMEOUT,
                ),
                verifier=LLMVerifier(),
                fusion=EvidenceFusion(),
                policy=PolicyEngine(),
            )

            result = await resolver.resolve(
                settlement
            )

        latency = (
            time.perf_counter()
            - start
        )

        return HybridBenchmarkResult(
            settlement_id=settlement.settlement_id,
            expected=expected,
            action=result.action.value,
            candidate_ids=list(
                result.candidate_ids
            ),
            confidence=result.confidence,
            evidence_codes=list(
                result.evidence_codes
            ),
            reason=result.reason,
            llm_invoked=result.llm_invoked,
            latency_seconds=latency,
        )

    except Exception as exc:
        latency = (
            time.perf_counter()
            - start
        )

        return HybridBenchmarkResult(
            settlement_id=settlement.settlement_id,
            expected=expected,
            action=None,
            candidate_ids=[],
            confidence=None,
            evidence_codes=[],
            reason=None,
            llm_invoked=False,
            latency_seconds=latency,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )


# -------------------------------------------------------------------
# Metrics
# -------------------------------------------------------------------

def calculate_metrics(
    results: list[HybridBenchmarkResult],
) -> dict[str, float]:

    total = len(results)

    if total == 0:
        return {
            "resolution_accuracy": 0.0,
            "auto_match_precision": 0.0,
            "auto_match_recall": 0.0,
            "false_auto_match_rate": 0.0,
            "automation_rate": 0.0,
            "human_review_rate": 0.0,
            "no_match_rate": 0.0,
            "failure_rate": 0.0,
            "average_latency": 0.0,
            "p50_latency": 0.0,
            "p95_latency": 0.0,
            "llm_invocation_rate": 0.0,
            "llm_invocation_count": 0,
        }

    successful = [
        result
        for result in results
        if result.error_type is None
    ]

    successful_count = len(successful)

    correct_resolutions = sum(
        1
        for result in results
        if resolution_is_correct(result)
    )

    auto_matches = [
        result
        for result in results
        if is_auto_match(result)
    ]

    correct_auto_matches = [
        result
        for result in auto_matches
        if auto_match_is_correct(result)
    ]

    false_auto_matches = [
        result
        for result in auto_matches
        if not auto_match_is_correct(result)
    ]

    positive_records = [
        result
        for result in results
        if result.expected is not None
    ]

    llm_invocation_count = sum(
        1
        for result in results
        if (
            result.error_type is None
            and result.llm_invoked
        )
    )

    human_review_count = sum(
        1
        for result in results
        if result.action
        == PolicyAction.HUMAN_REVIEW.value
    )

    no_match_count = sum(
        1
        for result in results
        if result.action
        == PolicyAction.NO_MATCH.value
    )

    failure_count = (
        total - successful_count
    )

    auto_match_precision = (
        len(correct_auto_matches)
        / len(auto_matches)
        if auto_matches
        else 0.0
    )

    auto_match_recall = (
        len(correct_auto_matches)
        / len(positive_records)
        if positive_records
        else 0.0
    )

    false_auto_match_rate = (
        len(false_auto_matches)
        / total
    )

    resolution_accuracy = (
        correct_resolutions
        / total
    )

    automation_rate = (
        len(auto_matches)
        / total
    )

    human_review_rate = (
        human_review_count
        / total
    )

    no_match_rate = (
        no_match_count
        / total
    )

    failure_rate = (
        failure_count
        / total
    )

    latencies = [
        result.latency_seconds
        for result in successful
    ]

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
        ordered = sorted(latencies)

        index = min(
            len(ordered) - 1,
            max(
                0,
                int(
                    len(ordered) * 0.95
                ) - 1,
            ),
        )

        p95_latency = ordered[index]

    llm_invocation_rate = (
        llm_invocation_count
        / total
    )

    return {
        "resolution_accuracy": resolution_accuracy,
        "auto_match_precision": auto_match_precision,
        "auto_match_recall": auto_match_recall,
        "false_auto_match_rate": false_auto_match_rate,
        "automation_rate": automation_rate,
        "human_review_rate": human_review_rate,
        "no_match_rate": no_match_rate,
        "failure_rate": failure_rate,
        "average_latency": average_latency,
        "p50_latency": p50_latency,
        "p95_latency": p95_latency,
        "llm_invocation_rate": llm_invocation_rate,
        "llm_invocation_count": llm_invocation_count,
    }


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

async def main() -> None:

    if BENCHMARK_FRESH and RESULTS_FILE.exists():
        RESULTS_FILE.unlink()

        print(
            "Fresh benchmark requested: "
            "previous Hybrid v2 results removed."
        )

    settlements = load_settlements()
    ground_truth = load_ground_truth()

    settlements = settlements[
        :BENCHMARK_LIMIT
    ]

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
        f"Starting Hybrid benchmark: "
        f"{total} records"
    )
    print(
        "Provider: Ollama"
    )
    print(
        f"Model: {MODEL}"
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

    if not pending_settlements:
        print("No pending records.")

    current_results: list[
        HybridBenchmarkResult
    ] = []

    benchmark_start = (
        time.perf_counter()
    )

    for index, settlement in enumerate(
        pending_settlements,
        start=1,
    ):
        expected = ground_truth[
            settlement.settlement_id
        ]

        result = await resolve_one(
            settlement=settlement,
            expected=expected,
        )

        current_results.append(result)

        if result.error_type is None:
            persist_result(result)

        completed = (
            len(persisted_results)
            + index
        )

        print(
            f"\rCompleted "
            f"{completed}/{total}",
            end="",
            flush=True,
        )

    print()

    benchmark_elapsed = (
        time.perf_counter()
        - benchmark_start
    )

    # ---------------------------------------------------------------
    # Combine persisted + current results.
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

    metrics = calculate_metrics(
        all_results
    )

    successful_results = [
        result
        for result in all_results
        if result.error_type is None
    ]

    failure_count = (
        len(all_results)
        - len(successful_results)
    )

    action_counts: dict[str, int] = {}

    for result in successful_results:
        action = result.action

        action_counts[action] = (
            action_counts.get(action, 0)
            + 1
        )

    # ---------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------

    print()
    print()
    print(
        "Hybrid Reconciliation Benchmark"
    )
    print(
        "--------------------------------"
    )
    print(
        f"Model               : {MODEL}"
    )
    print(
        f"Records evaluated   : "
        f"{len(all_results)}"
    )
    print(
        f"Successful requests : "
        f"{len(successful_results)}"
    )
    print(
        f"Failures            : "
        f"{failure_count}"
    )
    print()

    print(
        "Resolution Quality"
    )
    print(
        "------------------"
    )
    print(
        f"Resolution accuracy : "
        f"{metrics['resolution_accuracy']:.2%}"
    )
    print(
        f"Auto-match precision: "
        f"{metrics['auto_match_precision']:.2%}"
    )
    print(
        f"Auto-match recall   : "
        f"{metrics['auto_match_recall']:.2%}"
    )
    print(
        f"False-auto-match rate: "
        f"{metrics['false_auto_match_rate']:.2%}"
    )

    print()

    print(
        "Operational Outcomes"
    )
    print(
        "--------------------"
    )
    print(
        f"Automation rate     : "
        f"{metrics['automation_rate']:.2%}"
    )
    print(
        f"Human-review rate   : "
        f"{metrics['human_review_rate']:.2%}"
    )
    print(
        f"No-match rate       : "
        f"{metrics['no_match_rate']:.2%}"
    )
    print(
        f"Failure rate        : "
        f"{metrics['failure_rate']:.2%}"
    )
    print()

    print(
        "LLM Usage"
    )
    print(
        "---------"
    )
    print(
        f"LLM invocations     : "
        f"{metrics['llm_invocation_count']}"
    )
    print(
        f"LLM invocation rate : "
        f"{metrics['llm_invocation_rate']:.2%}"
    )
    print()

    print(
        "Actions"
    )
    print(
        "-------"
    )

    for action in sorted(
        action_counts,
        key=str,
    ):
        print(
            f"{action:<16}: "
            f"{action_counts[action]}"
        )

    print()

    print(
        "Latency"
    )
    print(
        "-------"
    )
    print(
        f"Average             : "
        f"{metrics['average_latency'] * 1000:.2f} ms"
    )
    print(
        f"P50                 : "
        f"{metrics['p50_latency'] * 1000:.2f} ms"
    )
    print(
        f"P95                 : "
        f"{metrics['p95_latency'] * 1000:.2f} ms"
    )

    print()

    print(
        f"Total benchmark time: "
        f"{benchmark_elapsed:.2f} sec"
    )

    print(
        f"Results file        : "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())