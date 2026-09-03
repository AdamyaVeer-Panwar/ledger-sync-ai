from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path("data")
RESULTS_DIR = Path("evaluation/results")

RULES_RESULTS_FILE = (
    RESULTS_DIR / "rules_baseline_results_v1.jsonl"
)

LLM_RESULTS_FILE = (
    RESULTS_DIR / "ollama_baseline_results_v3.jsonl"
)

HYBRID_RESULTS_FILE = (
    RESULTS_DIR / "hybrid_baseline_results_v2.jsonl"
)

GROUND_TRUTH_FILE = (
    DATA_DIR / "ground_truth.json"
)

SCENARIO_MANIFEST_FILE = (
    DATA_DIR / "scenario_manifest.json"
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Ollama is running locally in the current experiment.
#
# Therefore the observed API cost is zero.
#
# Keep these configurable so a hosted provider can be modeled later.

INPUT_COST_PER_1M_TOKENS = 0.0
OUTPUT_COST_PER_1M_TOKENS = 0.0


# ---------------------------------------------------------------------------
# Normalized record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvaluationRecord:
    settlement_id: str
    expected: list[str] | None
    prediction: list[str]

    decision: str

    confidence: float | None
    latency_seconds: float

    correct: bool
    automated: bool

    error_type: str | None


# ---------------------------------------------------------------------------
# Evaluation report models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Metrics:
    records: int

    # General correctness
    accuracy: float
    precision: float
    recall: float
    false_match_rate: float

    # Automation safety
    false_auto_match_rate: float
    auto_match_precision: float
    correct_automation_rate: float

    # Operational outcome
    exception_rate: float
    automation_rate: float
    failure_rate: float

    # Performance
    throughput_records_per_second: float
    average_latency_seconds: float
    p50_latency_seconds: float
    p95_latency_seconds: float

    # LLM usage
    llm_invocation_rate: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_llm_cost: float


@dataclass(frozen=True)
class ScenarioMetrics:
    scenario: str
    records: int

    accuracy: float
    precision: float
    recall: float
    false_match_rate: float

    # Automation safety
    false_auto_match_rate: float
    auto_match_precision: float
    correct_automation_rate: float

    exception_rate: float
    automation_rate: float
    failure_rate: float

    average_latency_seconds: float
    p50_latency_seconds: float
    p95_latency_seconds: float

    llm_invocation_rate: float


@dataclass(frozen=True)
class EvaluationReport:
    overall: Metrics
    by_scenario: dict[str, ScenarioMetrics]


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Required JSON file does not exist: {path}"
        )

    with path.open(
        encoding="utf-8",
    ) as file:
        return json.load(file)


def _load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required JSONL file does not exist: {path}"
        )

    records: list[dict[str, Any]] = []

    with path.open(
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
                value = json.loads(line)

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path} "
                    f"at line {line_number}: {exc}"
                ) from exc

            if not isinstance(value, dict):
                raise ValueError(
                    f"Expected JSON object in {path} "
                    f"at line {line_number}"
                )

            records.append(value)

    return records


# ---------------------------------------------------------------------------
# Dataset validation
# ---------------------------------------------------------------------------

def load_ground_truth() -> dict[
    str,
    list[str] | None,
]:
    data = _load_json(
        GROUND_TRUTH_FILE
    )

    if not isinstance(data, dict):
        raise ValueError(
            "ground_truth.json must contain an object"
        )

    normalized: dict[
        str,
        list[str] | None,
    ] = {}

    for settlement_id, expected in data.items():
        settlement_id = str(settlement_id)

        if expected is None:
            normalized[settlement_id] = None
            continue

        if not isinstance(expected, list):
            raise ValueError(
                f"Ground truth for {settlement_id} "
                "must be a list or null"
            )

        normalized[settlement_id] = [
            str(candidate_id)
            for candidate_id in expected
        ]

    return normalized


def load_scenario_manifest() -> dict[str, str]:
    data = _load_json(
        SCENARIO_MANIFEST_FILE
    )

    if not isinstance(data, dict):
        raise ValueError(
            "scenario_manifest.json must contain an object"
        )

    return {
        str(settlement_id): str(scenario)
        for settlement_id, scenario in data.items()
    }


def validate_dataset_identity(
    *,
    ground_truth: dict[str, list[str] | None],
    scenarios: dict[str, str],
    result_sets: dict[
        str,
        list[dict[str, Any]],
    ],
) -> None:
    expected_ids = set(
        ground_truth
    )

    scenario_ids = set(
        scenarios
    )

    # -----------------------------------------------------------------------
    # Ground truth <-> scenario manifest
    # -----------------------------------------------------------------------

    if expected_ids != scenario_ids:
        missing_scenarios = (
            expected_ids - scenario_ids
        )

        extra_scenarios = (
            scenario_ids - expected_ids
        )

        raise ValueError(
            "Ground truth and scenario manifest "
            "do not describe the same settlement universe. "
            f"Missing scenarios: {len(missing_scenarios)}, "
            f"extra scenarios: {len(extra_scenarios)}."
        )

    # -----------------------------------------------------------------------
    # Every benchmark result set must describe exactly the same universe.
    # -----------------------------------------------------------------------

    for name, records in result_sets.items():
        result_ids: set[str] = set()

        for record in records:
            if "settlement_id" not in record:
                raise ValueError(
                    f"{name} contains a result without "
                    "settlement_id."
                )

            result_ids.add(
                str(record["settlement_id"])
            )

        if result_ids != expected_ids:
            missing = (
                expected_ids - result_ids
            )

            extra = (
                result_ids - expected_ids
            )

            raise ValueError(
                f"{name} result set does not match "
                f"ground-truth settlement universe. "
                f"Missing: {len(missing)}, "
                f"extra: {len(extra)}."
            )

        if len(records) != len(result_ids):
            raise ValueError(
                f"{name} contains duplicate settlement IDs."
            )


# ---------------------------------------------------------------------------
# Candidate-set correctness
# ---------------------------------------------------------------------------

def candidate_sets_equal(
    actual: list[str],
    expected: list[str] | None,
) -> bool:
    """
    Compare reconciliation candidate sets without considering ordering.

    Positive ground truth:
        predicted candidate IDs must exactly equal expected IDs.

    Negative ground truth:
        prediction must be empty.
    """

    actual_set = set(actual)

    if expected is None:
        return not actual_set

    return actual_set == set(expected)


def is_positive_case(
    expected: list[str] | None,
) -> bool:
    return expected is not None


# ---------------------------------------------------------------------------
# Result normalization helpers
# ---------------------------------------------------------------------------

def _normalize_prediction(
    value: Any,
) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    if not isinstance(value, list):
        raise ValueError(
            "candidate_ids must be a list"
        )

    return [
        str(candidate_id)
        for candidate_id in value
    ]


def _normalize_error_type(
    value: Any,
) -> str | None:
    if value is None:
        return None

    return str(value)


def _normalize_confidence(
    value: Any,
) -> float | None:
    if value is None:
        return None

    return float(value)


def _build_evaluation_record(
    *,
    record: dict[str, Any],
    ground_truth: dict[str, list[str] | None],
    decision: str,
) -> EvaluationRecord:
    if "settlement_id" not in record:
        raise ValueError(
            "Benchmark result is missing settlement_id"
        )

    settlement_id = str(
        record["settlement_id"]
    )

    if settlement_id not in ground_truth:
        raise ValueError(
            f"Unknown settlement_id: {settlement_id}"
        )

    expected = ground_truth[
        settlement_id
    ]

    prediction = _normalize_prediction(
        record.get(
            "candidate_ids",
            [],
        )
    )

    error_type = _normalize_error_type(
        record.get("error_type")
    )

    correct = (
        error_type is None
        and candidate_sets_equal(
            prediction,
            expected,
        )
    )

    # -----------------------------------------------------------------------
    # An automated decision means that the system actually authorized
    # a candidate set, rather than merely making a prediction.
    #
    # We deliberately require a non-empty candidate set here because
    # NO_MATCH is an operationally different outcome.
    # -----------------------------------------------------------------------

    automated = (
        error_type is None
        and bool(prediction)
        and decision in {
            "MATCHED_RULE",
            "MATCH",
            "AUTO_MATCH",
        }
    )

    latency_seconds = float(
        record.get(
            "latency_seconds",
            0.0,
        )
    )

    if latency_seconds < 0:
        raise ValueError(
            f"Negative latency for {settlement_id}"
        )

    return EvaluationRecord(
        settlement_id=settlement_id,
        expected=expected,
        prediction=prediction,
        decision=decision,
        confidence=_normalize_confidence(
            record.get("confidence")
        ),
        latency_seconds=latency_seconds,
        correct=correct,
        automated=automated,
        error_type=error_type,
    )


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize_rules(
    records: list[dict[str, Any]],
    ground_truth: dict[str, list[str] | None],
) -> list[EvaluationRecord]:
    return [
        _build_evaluation_record(
            record=record,
            ground_truth=ground_truth,
            decision=str(
                record.get(
                    "decision",
                    "ERROR",
                )
            ),
        )
        for record in records
    ]


def normalize_llm(
    records: list[dict[str, Any]],
    ground_truth: dict[str, list[str] | None],
) -> list[EvaluationRecord]:
    return [
        _build_evaluation_record(
            record=record,
            ground_truth=ground_truth,
            decision=str(
                record.get(
                    "decision",
                    "ERROR",
                )
            ),
        )
        for record in records
    ]


def normalize_hybrid(
    records: list[dict[str, Any]],
    ground_truth: dict[str, list[str] | None],
) -> list[EvaluationRecord]:
    return [
        _build_evaluation_record(
            record=record,
            ground_truth=ground_truth,
            decision=str(
                record.get(
                    "action",
                    "ERROR",
                )
            ),
        )
        for record in records
    ]


# ---------------------------------------------------------------------------
# Latency
# ---------------------------------------------------------------------------

def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    if not values:
        return 0.0

    if not 0.0 <= percentile_value <= 100.0:
        raise ValueError(
            "percentile_value must be between 0 and 100"
        )

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    rank = (
        percentile_value
        / 100.0
        * (len(ordered) - 1)
    )

    lower = int(rank)

    upper = min(
        lower + 1,
        len(ordered) - 1,
    )

    weight = (
        rank - lower
    )

    return (
        ordered[lower]
        + (
            ordered[upper]
            - ordered[lower]
        )
        * weight
    )


# ---------------------------------------------------------------------------
# LLM usage
# ---------------------------------------------------------------------------

def llm_usage(
    raw_llm_records: list[dict[str, Any]],
) -> tuple[int, int, int]:
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    for record in raw_llm_records:
        record_input = int(
            record.get(
                "input_tokens",
                0,
            )
        )

        record_output = int(
            record.get(
                "output_tokens",
                0,
            )
        )

        if record_input < 0 or record_output < 0:
            raise ValueError(
                "Token counts cannot be negative"
            )

        record_total = int(
            record.get(
                "total_tokens",
                record_input + record_output,
            )
        )

        if record_total < 0:
            raise ValueError(
                "Total token count cannot be negative"
            )

        input_tokens += record_input
        output_tokens += record_output
        total_tokens += record_total

    return (
        input_tokens,
        output_tokens,
        total_tokens,
    )


def estimate_llm_cost(
    input_tokens: int,
    output_tokens: int,
) -> float:
    input_cost = (
        input_tokens
        / 1_000_000
        * INPUT_COST_PER_1M_TOKENS
    )

    output_cost = (
        output_tokens
        / 1_000_000
        * OUTPUT_COST_PER_1M_TOKENS
    )

    return (
        input_cost
        + output_cost
    )


# ---------------------------------------------------------------------------
# LLM invocation detection for Hybrid
# ---------------------------------------------------------------------------

def hybrid_llm_invocation_set(
    raw_hybrid_records: list[dict[str, Any]],
) -> set[str]:
    return {
        str(record["settlement_id"])
        for record in raw_hybrid_records
        if (
            record.get("error_type") is None
            and bool(record.get("llm_invoked", False))
        )
    }


def hybrid_llm_invocation_count(
    raw_hybrid_records: list[dict[str, Any]],
) -> int:
    return len(
        hybrid_llm_invocation_set(
            raw_hybrid_records
        )
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def calculate_metrics(
    records: list[EvaluationRecord],
    *,
    llm_invocations: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    benchmark_elapsed_seconds: float | None = None,
) -> Metrics:
    total = len(records)

    if total == 0:
        return Metrics(
            records=0,

            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            false_match_rate=0.0,

            false_auto_match_rate=0.0,
            auto_match_precision=0.0,
            correct_automation_rate=0.0,

            exception_rate=0.0,
            automation_rate=0.0,
            failure_rate=0.0,

            throughput_records_per_second=0.0,

            average_latency_seconds=0.0,
            p50_latency_seconds=0.0,
            p95_latency_seconds=0.0,

            llm_invocation_rate=0.0,

            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,

            estimated_llm_cost=estimate_llm_cost(
                input_tokens,
                output_tokens,
            ),
        )

    if llm_invocations < 0:
        raise ValueError(
            "llm_invocations cannot be negative"
        )

    if (
        llm_invocations > total
    ):
        raise ValueError(
            "llm_invocations cannot exceed record count"
        )

    # -----------------------------------------------------------------------
    # Basic populations
    # -----------------------------------------------------------------------

    failures = sum(
        1
        for record in records
        if record.error_type is not None
    )

    successful_records = [
        record
        for record in records
        if record.error_type is None
    ]

    correct_records = sum(
        1
        for record in records
        if record.correct
    )

    positive_records = [
        record
        for record in records
        if is_positive_case(
            record.expected
        )
    ]

    predicted_positive_records = [
        record
        for record in records
        if bool(record.prediction)
    ]

    # -----------------------------------------------------------------------
    # Record-level confusion matrix
    #
    # This is intentionally record based rather than candidate based.
    #
    # Example:
    #   expected = ["L001", "L002"]
    #
    # is treated as one positive reconciliation case.
    # -----------------------------------------------------------------------

    true_positives = sum(
        1
        for record in records
        if (
            bool(record.prediction)
            and record.expected is not None
            and record.correct
        )
    )

    false_positives = sum(
        1
        for record in records
        if (
            bool(record.prediction)
            and record.expected is None
        )
    )

    false_negatives = sum(
        1
        for record in records
        if (
            record.expected is not None
            and not record.correct
        )
    )

    # -----------------------------------------------------------------------
    # Automation safety
    #
    # These metrics answer a different question from normal precision:
    #
    # "When the system actually automated a financial decision,
    # how safe was that automation?"
    # -----------------------------------------------------------------------

    auto_matches = [
        record
        for record in records
        if record.automated
    ]

    correct_auto_matches = [
        record
        for record in auto_matches
        if record.correct
    ]

    false_auto_matches = [
        record
        for record in auto_matches
        if not record.correct
    ]

    false_auto_match_rate = (
        len(false_auto_matches)
        / total
        if total
        else 0.0
    )

    auto_match_precision = (
        len(correct_auto_matches)
        / len(auto_matches)
        if auto_matches
        else 0.0
    )

    correct_automation_rate = (
        len(correct_auto_matches)
        / total
        if total
        else 0.0
    )

    # -----------------------------------------------------------------------
    # Accuracy
    # -----------------------------------------------------------------------

    accuracy = (
        correct_records
        / total
    )

    # -----------------------------------------------------------------------
    # General precision
    #
    # Among records where the system predicted a candidate set,
    # how many candidate predictions were correct?
    # -----------------------------------------------------------------------

    precision = (
        true_positives
        / len(predicted_positive_records)
        if predicted_positive_records
        else 0.0
    )

    # -----------------------------------------------------------------------
    # Recall
    #
    # Among all positive ground-truth reconciliation records,
    # how many were resolved correctly?
    # -----------------------------------------------------------------------

    recall = (
        true_positives
        / len(positive_records)
        if positive_records
        else 0.0
    )

    # -----------------------------------------------------------------------
    # False-match rate
    #
    # Negative case predicted as a candidate match.
    #
    # This is NOT the same as false_auto_match_rate:
    #
    # false_match_rate:
    #     false positive prediction
    #
    # false_auto_match_rate:
    #     incorrect automated authorization
    # -----------------------------------------------------------------------

    false_match_rate = (
        false_positives
        / total
    )

    # -----------------------------------------------------------------------
    # Exception / automation populations
    # -----------------------------------------------------------------------

    exception_count = sum(
        1
        for record in records
        if (
            record.error_type is not None
            or record.decision
            in {
                "HUMAN_REVIEW",
                "NO_MATCH",
            }
        )
    )

    automation_count = sum(
        1
        for record in records
        if record.automated
    )

    exception_rate = (
        exception_count
        / total
    )

    automation_rate = (
        automation_count
        / total
    )

    failure_rate = (
        failures
        / total
    )

    # -----------------------------------------------------------------------
    # Latency
    #
    # Failed requests are excluded from successful latency statistics.
    # -----------------------------------------------------------------------

    latencies = [
        record.latency_seconds
        for record in successful_records
    ]

    average_latency = (
        statistics.mean(latencies)
        if latencies
        else 0.0
    )

    p50_latency = percentile(
        latencies,
        50.0,
    )

    p95_latency = percentile(
        latencies,
        95.0,
    )

    # -----------------------------------------------------------------------
    # Throughput
    #
    # Prefer measured benchmark wall-clock duration when available.
    #
    # Otherwise fall back to sum of successful per-record latencies.
    # -----------------------------------------------------------------------

    if (
        benchmark_elapsed_seconds is not None
        and benchmark_elapsed_seconds > 0
    ):
        throughput = (
            total
            / benchmark_elapsed_seconds
        )

    else:
        total_latency = sum(
            latencies
        )

        throughput = (
            total
            / total_latency
            if total_latency > 0
            else 0.0
        )

    # -----------------------------------------------------------------------
    # LLM metrics
    # -----------------------------------------------------------------------

    llm_invocation_rate = (
        llm_invocations
        / total
    )

    estimated_cost = estimate_llm_cost(
        input_tokens,
        output_tokens,
    )

    return Metrics(
        records=total,

        accuracy=accuracy,
        precision=precision,
        recall=recall,
        false_match_rate=false_match_rate,

        false_auto_match_rate=(
            false_auto_match_rate
        ),
        auto_match_precision=(
            auto_match_precision
        ),
        correct_automation_rate=(
            correct_automation_rate
        ),

        exception_rate=exception_rate,
        automation_rate=automation_rate,
        failure_rate=failure_rate,

        throughput_records_per_second=throughput,

        average_latency_seconds=(
            average_latency
        ),
        p50_latency_seconds=(
            p50_latency
        ),
        p95_latency_seconds=(
            p95_latency
        ),

        llm_invocation_rate=(
            llm_invocation_rate
        ),

        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,

        estimated_llm_cost=estimated_cost,
    )


# ---------------------------------------------------------------------------
# Scenario metrics
# ---------------------------------------------------------------------------

def calculate_scenario_metrics(
    records: list[EvaluationRecord],
    scenarios: dict[str, str],
    *,
    llm_invocations_by_settlement: set[str] | None = None,
) -> dict[str, ScenarioMetrics]:
    grouped: dict[
        str,
        list[EvaluationRecord],
    ] = {}

    # -----------------------------------------------------------------------
    # Group records by scenario.
    # -----------------------------------------------------------------------

    for record in records:
        if record.settlement_id not in scenarios:
            raise ValueError(
                "Missing scenario for settlement "
                f"{record.settlement_id}"
            )

        scenario = scenarios[
            record.settlement_id
        ]

        grouped.setdefault(
            scenario,
            [],
        ).append(record)

    # -----------------------------------------------------------------------
    # Produce metrics per scenario.
    # -----------------------------------------------------------------------

    reports: dict[
        str,
        ScenarioMetrics,
    ] = {}

    for scenario, scenario_records in sorted(
        grouped.items()
    ):
        invocation_count = 0

        if (
            llm_invocations_by_settlement
            is not None
        ):
            invocation_count = sum(
                1
                for record in scenario_records
                if record.settlement_id
                in llm_invocations_by_settlement
            )

        metrics = calculate_metrics(
            scenario_records,
            llm_invocations=invocation_count,
        )

        reports[scenario] = ScenarioMetrics(
            scenario=scenario,
            records=metrics.records,

            accuracy=metrics.accuracy,
            precision=metrics.precision,
            recall=metrics.recall,
            false_match_rate=(
                metrics.false_match_rate
            ),

            false_auto_match_rate=(
                metrics.false_auto_match_rate
            ),
            auto_match_precision=(
                metrics.auto_match_precision
            ),
            correct_automation_rate=(
                metrics.correct_automation_rate
            ),

            exception_rate=(
                metrics.exception_rate
            ),
            automation_rate=(
                metrics.automation_rate
            ),
            failure_rate=(
                metrics.failure_rate
            ),

            average_latency_seconds=(
                metrics.average_latency_seconds
            ),
            p50_latency_seconds=(
                metrics.p50_latency_seconds
            ),
            p95_latency_seconds=(
                metrics.p95_latency_seconds
            ),

            llm_invocation_rate=(
                metrics.llm_invocation_rate
            ),
        )

    return reports


# ---------------------------------------------------------------------------
# Public evaluator
# ---------------------------------------------------------------------------

def evaluate_system(
    *,
    records: list[EvaluationRecord],
    scenarios: dict[str, str],
    llm_invocations: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    benchmark_elapsed_seconds: float | None = None,
    llm_invocations_by_settlement: set[str] | None = None,
) -> EvaluationReport:
    overall = calculate_metrics(
        records,
        llm_invocations=llm_invocations,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        benchmark_elapsed_seconds=(
            benchmark_elapsed_seconds
        ),
    )

    by_scenario = calculate_scenario_metrics(
        records,
        scenarios,
        llm_invocations_by_settlement=(
            llm_invocations_by_settlement
        ),
    )

    return EvaluationReport(
        overall=overall,
        by_scenario=by_scenario,
    )


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def metric_delta(
    after: Metrics,
    before: Metrics,
) -> dict[str, float]:
    """
    Compute before -> after changes.

    Positive values mean the metric increased.
    For metrics such as false-match/error rates, a negative delta
    is therefore usually an improvement.
    """

    return {
        # Correctness
        "accuracy": (
            after.accuracy
            - before.accuracy
        ),
        "precision": (
            after.precision
            - before.precision
        ),
        "recall": (
            after.recall
            - before.recall
        ),
        "false_match_rate": (
            after.false_match_rate
            - before.false_match_rate
        ),

        # Automation safety
        "false_auto_match_rate": (
            after.false_auto_match_rate
            - before.false_auto_match_rate
        ),
        "auto_match_precision": (
            after.auto_match_precision
            - before.auto_match_precision
        ),
        "correct_automation_rate": (
            after.correct_automation_rate
            - before.correct_automation_rate
        ),

        # Operational outcomes
        "exception_rate": (
            after.exception_rate
            - before.exception_rate
        ),
        "automation_rate": (
            after.automation_rate
            - before.automation_rate
        ),
        "failure_rate": (
            after.failure_rate
            - before.failure_rate
        ),

        # Performance
        "throughput_records_per_second": (
            after.throughput_records_per_second
            - before.throughput_records_per_second
        ),
        "average_latency_seconds": (
            after.average_latency_seconds
            - before.average_latency_seconds
        ),
        "p50_latency_seconds": (
            after.p50_latency_seconds
            - before.p50_latency_seconds
        ),
        "p95_latency_seconds": (
            after.p95_latency_seconds
            - before.p95_latency_seconds
        ),

        # LLM
        "llm_invocation_rate": (
            after.llm_invocation_rate
            - before.llm_invocation_rate
        ),
        "estimated_llm_cost": (
            after.estimated_llm_cost
            - before.estimated_llm_cost
        ),
    }


# ---------------------------------------------------------------------------
# Convenience loader
# ---------------------------------------------------------------------------

def load_all_inputs() -> dict[str, Any]:
    ground_truth = load_ground_truth()

    scenarios = load_scenario_manifest()

    raw_rules = _load_jsonl(
        RULES_RESULTS_FILE
    )

    raw_llm = _load_jsonl(
        LLM_RESULTS_FILE
    )

    raw_hybrid = _load_jsonl(
        HYBRID_RESULTS_FILE
    )

    validate_dataset_identity(
        ground_truth=ground_truth,
        scenarios=scenarios,
        result_sets={
            "Rules": raw_rules,
            "LLM": raw_llm,
            "Hybrid": raw_hybrid,
        },
    )

    rules = normalize_rules(
        raw_rules,
        ground_truth,
    )

    llm = normalize_llm(
        raw_llm,
        ground_truth,
    )

    hybrid = normalize_hybrid(
        raw_hybrid,
        ground_truth,
    )

    return {
        "ground_truth": ground_truth,
        "scenarios": scenarios,

        "raw_rules": raw_rules,
        "raw_llm": raw_llm,
        "raw_hybrid": raw_hybrid,

        "rules": rules,
        "llm": llm,
        "hybrid": hybrid,
    }

@dataclass(frozen=True)
class ScenarioRegression:
    scenario: str

    before_accuracy: float
    after_accuracy: float
    accuracy_delta: float

    before_automation_rate: float
    after_automation_rate: float
    automation_delta: float

    before_false_auto_match_rate: float
    after_false_auto_match_rate: float
    false_auto_match_delta: float

    before_precision: float
    after_precision: float
    precision_delta: float

    before_recall: float
    after_recall: float
    recall_delta: float

    regressed: bool


@dataclass(frozen=True)
class RegressionReport:
    before: Metrics
    after: Metrics

    accuracy_delta: float
    precision_delta: float
    recall_delta: float
    false_match_rate_delta: float

    automation_delta: float
    correct_automation_delta: float
    auto_match_precision_delta: float
    false_auto_match_rate_delta: float

    scenario_regressions: dict[
        str,
        ScenarioRegression,
    ]

    regressions_detected: int


def compare_reports(
    before: EvaluationReport,
    after: EvaluationReport,
) -> RegressionReport:
    before_metrics = before.overall
    after_metrics = after.overall

    scenario_names = sorted(
        set(before.by_scenario)
        | set(after.by_scenario)
    )

    scenario_regressions: dict[
        str,
        ScenarioRegression,
    ] = {}

    for scenario in scenario_names:
        before_scenario = before.by_scenario.get(
            scenario
        )

        after_scenario = after.by_scenario.get(
            scenario
        )

        if before_scenario is None:
            before_accuracy = 0.0
            before_automation = 0.0
            before_false_auto = 0.0
            before_precision = 0.0
            before_recall = 0.0
        else:
            before_accuracy = (
                before_scenario.accuracy
            )

            before_automation = (
                before_scenario.automation_rate
            )

            before_false_auto = (
                before_scenario.false_auto_match_rate
            )

            before_precision = (
                before_scenario.precision
            )

            before_recall = (
                before_scenario.recall
            )

        if after_scenario is None:
            after_accuracy = 0.0
            after_automation = 0.0
            after_false_auto = 0.0
            after_precision = 0.0
            after_recall = 0.0
        else:
            after_accuracy = (
                after_scenario.accuracy
            )

            after_automation = (
                after_scenario.automation_rate
            )

            after_false_auto = (
                after_scenario.false_auto_match_rate
            )

            after_precision = (
                after_scenario.precision
            )

            after_recall = (
                after_scenario.recall
            )

        accuracy_delta = (
            after_accuracy
            - before_accuracy
        )

        automation_delta = (
            after_automation
            - before_automation
        )

        false_auto_delta = (
            after_false_auto
            - before_false_auto
        )

        precision_delta = (
            after_precision
            - before_precision
        )

        recall_delta = (
            after_recall
            - before_recall
        )

        # ---------------------------------------------------------------
        # Regression policy
        #
        # A scenario is considered regressed when:
        #
        #   1. correctness decreases materially, OR
        #   2. false-auto-match rate increases.
        #
        # The second condition is especially important for financial
        # reconciliation: an automation safety degradation must not be
        # hidden by a gain in recall.
        # ---------------------------------------------------------------

        regressed = (
            accuracy_delta < -0.001
            or false_auto_delta > 0.001
        )

        scenario_regressions[
            scenario
        ] = ScenarioRegression(
            scenario=scenario,
            before_accuracy=before_accuracy,
            after_accuracy=after_accuracy,
            accuracy_delta=accuracy_delta,
            before_automation_rate=before_automation,
            after_automation_rate=after_automation,
            automation_delta=automation_delta,
            before_false_auto_match_rate=(
                before_false_auto
            ),
            after_false_auto_match_rate=(
                after_false_auto
            ),
            false_auto_match_delta=(
                false_auto_delta
            ),
            before_precision=before_precision,
            after_precision=after_precision,
            precision_delta=precision_delta,
            before_recall=before_recall,
            after_recall=after_recall,
            recall_delta=recall_delta,
            regressed=regressed,
        )

    regressions_detected = sum(
        regression.regressed
        for regression
        in scenario_regressions.values()
    )

    return RegressionReport(
        before=before_metrics,
        after=after_metrics,
        accuracy_delta=(
            after_metrics.accuracy
            - before_metrics.accuracy
        ),
        precision_delta=(
            after_metrics.precision
            - before_metrics.precision
        ),
        recall_delta=(
            after_metrics.recall
            - before_metrics.recall
        ),
        false_match_rate_delta=(
            after_metrics.false_match_rate
            - before_metrics.false_match_rate
        ),
        automation_delta=(
            after_metrics.automation_rate
            - before_metrics.automation_rate
        ),
        correct_automation_delta=(
            after_metrics.correct_automation_rate
            - before_metrics.correct_automation_rate
        ),
        auto_match_precision_delta=(
            after_metrics.auto_match_precision
            - before_metrics.auto_match_precision
        ),
        false_auto_match_rate_delta=(
            after_metrics.false_auto_match_rate
            - before_metrics.false_auto_match_rate
        ),
        scenario_regressions=(
            scenario_regressions
        ),
        regressions_detected=(
            regressions_detected
        ),
    )