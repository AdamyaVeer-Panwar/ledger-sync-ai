import json
from collections import defaultdict
from pathlib import Path


RESULTS_FILE = Path(
    "evaluation/results/ollama_baseline_results_v3.jsonl"
)


def load_results() -> list[dict]:
    results = []

    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"Results file not found: {RESULTS_FILE}"
        )

    with RESULTS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(
                    f"Warning: skipping malformed line: {exc}"
                )

    return results


def is_correct(result: dict) -> bool:
    expected = result.get("expected")
    decision = result.get("decision")
    predicted_ids = result.get("candidate_ids") or []

    if result.get("error_type") is not None:
        return False

    # Ground truth says NO_MATCH.
    if expected is None:
        return (
            decision == "NO_MATCH"
            and not predicted_ids
        )

    # Ground truth contains expected candidates.
    return (
        decision == "MATCH"
        and predicted_ids == expected
    )


def confidence_bucket(
    confidence: float | None,
) -> str:
    if confidence is None:
        return "NONE"

    if confidence < 0.50:
        return "0.00-0.49"

    if confidence < 0.60:
        return "0.50-0.59"

    if confidence < 0.70:
        return "0.60-0.69"

    if confidence < 0.80:
        return "0.70-0.79"

    if confidence < 0.90:
        return "0.80-0.89"

    if confidence < 0.95:
        return "0.90-0.94"

    if confidence < 1.00:
        return "0.95-0.99"

    return "1.00"


def main() -> None:
    results = load_results()

    buckets: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
        }
    )

    for result in results:
        confidence = result.get("confidence")
        bucket = confidence_bucket(confidence)

        buckets[bucket]["total"] += 1

        if is_correct(result):
            buckets[bucket]["correct"] += 1
        else:
            buckets[bucket]["incorrect"] += 1

    ordered_buckets = [
        "0.00-0.49",
        "0.50-0.59",
        "0.60-0.69",
        "0.70-0.79",
        "0.80-0.89",
        "0.90-0.94",
        "0.95-0.99",
        "1.00",
        "NONE",
    ]

    print()
    print("Ollama Confidence Calibration")
    print("-----------------------------")
    print(
        f"Records analyzed : {len(results)}"
    )
    print()

    print(
        f"{'Confidence':<15}"
        f"{'Total':>8}"
        f"{'Correct':>10}"
        f"{'Incorrect':>12}"
        f"{'Accuracy':>12}"
    )

    print("-" * 57)

    for bucket in ordered_buckets:
        stats = buckets.get(bucket)

        if not stats or stats["total"] == 0:
            continue

        total = stats["total"]
        correct = stats["correct"]
        incorrect = stats["incorrect"]

        accuracy = (
            correct / total
            if total
            else 0.0
        )

        print(
            f"{bucket:<15}"
            f"{total:>8}"
            f"{correct:>10}"
            f"{incorrect:>12}"
            f"{accuracy:>11.2%}"
        )

    print()

    # -------------------------------------------------------------
    # Special attention to confidence = 1.0
    # -------------------------------------------------------------

    perfect_confidence = [
        result
        for result in results
        if result.get("confidence") == 1.0
    ]

    perfect_correct = sum(
        is_correct(result)
        for result in perfect_confidence
    )

    perfect_incorrect = (
        len(perfect_confidence)
        - perfect_correct
    )

    print("Confidence = 1.0")
    print("-----------------")
    print(
        f"Total     : {len(perfect_confidence)}"
    )
    print(
        f"Correct   : {perfect_correct}"
    )
    print(
        f"Incorrect : {perfect_incorrect}"
    )

    if perfect_confidence:
        print(
            f"Accuracy  : "
            f"{perfect_correct / len(perfect_confidence):.2%}"
        )

    # -------------------------------------------------------------
    # Accuracy at possible thresholds.
    # -------------------------------------------------------------

    print()
    print("Threshold Analysis")
    print("------------------")

    for threshold in [
        0.70,
        0.80,
        0.85,
        0.90,
        0.95,
        0.99,
        1.00,
    ]:
        selected = [
            result
            for result in results
            if (
                result.get("confidence") is not None
                and result["confidence"] >= threshold
            )
        ]

        if not selected:
            continue

        correct = sum(
            is_correct(result)
            for result in selected
        )

        print(
            f"confidence >= {threshold:.2f}"
            f" | count={len(selected):>3}"
            f" | accuracy={correct / len(selected):.2%}"
        )


if __name__ == "__main__":
    main()