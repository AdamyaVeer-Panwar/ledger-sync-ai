import asyncio
import json
from collections import Counter, defaultdict
from pathlib import Path

from app.db.session import SessionFactory
from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.models import LedgerRecord
from app.domain.reconciliation.llm_verifier import (
    LLMVerifier,
    VerificationStatus,
)
from evaluation.benchmark_llm import (
    load_settlements,
    retrieve_candidates,
    to_domain_ledger,
)


RESULTS_FILE = Path(
    "evaluation/results/ollama_baseline_results_v3.jsonl"
)


def load_benchmark_results() -> dict[str, dict]:
    results = {}

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
                result = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"Warning: skipping malformed line: {exc}"
                )
                continue

            results[result["settlement_id"]] = result

    return results


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


def is_correct(result: dict) -> bool:
    expected = result.get("expected")
    decision = result.get("decision")
    predicted_ids = result.get(
        "candidate_ids"
    ) or []

    if result.get("error_type") is not None:
        return False

    if expected is None:
        return (
            decision == "NO_MATCH"
            and not predicted_ids
        )

    if decision != "MATCH":
        return False

    return set(predicted_ids) == set(expected)


async def analyze() -> None:
    benchmark_results = load_benchmark_results()
    settlements = load_settlements()

    settlements_by_id = {
        settlement.settlement_id: settlement
        for settlement in settlements
    }

    verifier = LLMVerifier()

    verification_counts = Counter()
    correctness_by_verification = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
        }
    )

    confidence_by_verification = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
        }
    )

    verification_confidence_matrix = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
        }
    )

    missing_settlements = []

    async with SessionFactory() as session:
        for settlement_id, result in benchmark_results.items():
            settlement = settlements_by_id.get(
                settlement_id
            )

            if settlement is None:
                missing_settlements.append(
                    settlement_id
                )
                continue

            orm_candidates = await retrieve_candidates(
                session=session,
                settlement=settlement,
            )

            candidates: list[LedgerRecord] = [
                to_domain_ledger(ledger)
                for ledger in orm_candidates
            ]

            resolution = AIResolution(
                decision=AIResolutionDecision(
                    result["decision"]
                ),
                candidate_ids=list(
                    result.get("candidate_ids")
                    or []
                ),
                confidence=float(
                    result.get("confidence", 0.0)
                ),
                evidence_codes=[],
            )

            verification = verifier.verify(
                settlement=settlement,
                candidates=candidates,
                resolution=resolution,
            )

            status = verification.status.value
            correct = is_correct(result)
            bucket = confidence_bucket(
                resolution.confidence
            )

            verification_counts[status] += 1

            verification_stats = (
                correctness_by_verification[status]
            )
            verification_stats["total"] += 1

            if correct:
                verification_stats["correct"] += 1
            else:
                verification_stats["incorrect"] += 1

            confidence_stats = (
                confidence_by_verification[status]
            )
            confidence_stats["total"] += 1

            if correct:
                confidence_stats["correct"] += 1
            else:
                confidence_stats["incorrect"] += 1

            matrix_key = (
                status,
                bucket,
            )

            matrix_stats = (
                verification_confidence_matrix[
                    matrix_key
                ]
            )

            matrix_stats["total"] += 1

            if correct:
                matrix_stats["correct"] += 1
            else:
                matrix_stats["incorrect"] += 1

    print()
    print("LLM Verification Analysis")
    print("-------------------------")
    print(
        f"V3 records analyzed : "
        f"{len(benchmark_results)}"
    )

    if missing_settlements:
        print(
            f"Missing settlements : "
            f"{len(missing_settlements)}"
        )

    print()

    print("Verification Status")
    print("-------------------")

    for status in (
        VerificationStatus.VERIFIED.value,
        VerificationStatus.REJECTED.value,
        VerificationStatus.UNVERIFIED.value,
    ):
        count = verification_counts[status]

        print(
            f"{status:<12}: {count:>3}"
        )

    print()

    print("Verification vs Ground Truth")
    print("----------------------------")

    print(
        f"{'Status':<14}"
        f"{'Total':>8}"
        f"{'Correct':>10}"
        f"{'Incorrect':>12}"
        f"{'Accuracy':>12}"
    )

    print("-" * 56)

    for status in (
        VerificationStatus.VERIFIED.value,
        VerificationStatus.REJECTED.value,
        VerificationStatus.UNVERIFIED.value,
    ):
        stats = correctness_by_verification[
            status
        ]

        total = stats["total"]

        accuracy = (
            stats["correct"] / total
            if total
            else 0.0
        )

        print(
            f"{status:<14}"
            f"{total:>8}"
            f"{stats['correct']:>10}"
            f"{stats['incorrect']:>12}"
            f"{accuracy:>11.2%}"
        )

    print()

    print(
        "Verification × Confidence"
    )
    print(
        "-------------------------"
    )

    print(
        f"{'Verification':<14}"
        f"{'Confidence':<15}"
        f"{'Total':>8}"
        f"{'Correct':>10}"
        f"{'Incorrect':>12}"
        f"{'Accuracy':>12}"
    )

    print("-" * 75)

    ordered_statuses = [
        VerificationStatus.VERIFIED.value,
        VerificationStatus.UNVERIFIED.value,
        VerificationStatus.REJECTED.value,
    ]

    ordered_buckets = [
        "0.00-0.49",
        "0.50-0.59",
        "0.60-0.69",
        "0.70-0.79",
        "0.80-0.89",
        "0.90-0.94",
        "0.95-0.99",
        "1.00",
    ]

    for status in ordered_statuses:
        for bucket in ordered_buckets:
            stats = (
                verification_confidence_matrix[
                    (status, bucket)
                ]
            )

            if stats["total"] == 0:
                continue

            total = stats["total"]

            accuracy = (
                stats["correct"] / total
                if total
                else 0.0
            )

            print(
                f"{status:<14}"
                f"{bucket:<15}"
                f"{total:>8}"
                f"{stats['correct']:>10}"
                f"{stats['incorrect']:>12}"
                f"{accuracy:>11.2%}"
            )

    print()


def main() -> None:
    asyncio.run(analyze())


if __name__ == "__main__":
    main()