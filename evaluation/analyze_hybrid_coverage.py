import asyncio
import json
from collections import Counter
from pathlib import Path

from app.db.session import SessionFactory
from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerifier,
)
from app.domain.reconciliation.rule_matcher import (
    RuleMatcher,
)
from app.domain.reconciliation.rule_result import (
    to_rule_match_result,
)
from evaluation.benchmark_llm import (
    load_settlements,
    retrieve_candidates,
    to_domain_ledger,
)


RESULTS_FILE = Path(
    "evaluation/results/ollama_baseline_results_v3.jsonl"
)


def load_results() -> dict[str, dict]:
    results: dict[str, dict] = {}

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
            except json.JSONDecodeError:
                continue

            results[result["settlement_id"]] = result

    return results


def is_correct(result: dict) -> bool:
    expected = result.get("expected")
    decision = result.get("decision")
    predicted_ids = set(
        result.get("candidate_ids") or []
    )

    if result.get("error_type") is not None:
        return False

    if expected is None:
        return (
            decision == "NO_MATCH"
            and not predicted_ids
        )

    if decision != "MATCH":
        return False

    return predicted_ids == set(expected)


def main() -> None:
    asyncio.run(analyze())


async def analyze() -> None:
    persisted_results = load_results()
    settlements = load_settlements()

    settlements_by_id = {
        settlement.settlement_id: settlement
        for settlement in settlements
    }

    rule_matcher = RuleMatcher()
    verifier = LLMVerifier()

    matrix: Counter[tuple[str, str, str]] = Counter()

    examples: dict[
        tuple[str, str, str],
        list[str],
    ] = {}

    async with SessionFactory() as session:
        for settlement_id, llm_result in persisted_results.items():
            settlement = settlements_by_id.get(
                settlement_id
            )

            if settlement is None:
                continue

            orm_candidates = await retrieve_candidates(
                session=session,
                settlement=settlement,
            )

            candidates = [
                to_domain_ledger(ledger)
                for ledger in orm_candidates
            ]

            rule_decision = rule_matcher.match(
                settlement=settlement,
                candidates=candidates,
            )

            rule_result = to_rule_match_result(
                rule_decision
            )

            ai_result = AIResolution(
                decision=AIResolutionDecision(
                    llm_result["decision"]
                ),
                candidate_ids=list(
                    llm_result.get(
                        "candidate_ids"
                    )
                    or []
                ),
                confidence=float(
                    llm_result.get(
                        "confidence",
                        0.0,
                    )
                ),
                evidence_codes=[],
            )

            verification = verifier.verify(
                settlement=settlement,
                candidates=candidates,
                resolution=ai_result,
            )

            rule_status = rule_result.status.value
            verification_status = (
                verification.status.value
            )

            correctness = (
                "CORRECT"
                if is_correct(llm_result)
                else "INCORRECT"
            )

            key = (
                rule_status,
                verification_status,
                correctness,
            )

            matrix[key] += 1

            examples.setdefault(
                (
                    rule_status,
                    verification_status,
                    correctness,
                ),
                [],
            )

            if len(
                examples[
                    (
                        rule_status,
                        verification_status,
                        correctness,
                    )
                ]
            ) < 5:
                examples[
                    (
                        rule_status,
                        verification_status,
                        correctness,
                    )
                ].append(settlement_id)

    print()
    print("Hybrid Coverage Analysis")
    print("=========================")

    print(
        f"Records analyzed : "
        f"{len(persisted_results)}"
    )

    print()

    print(
        f"{'Rule Result':<18}"
        f"{'Verification':<15}"
        f"{'Correctness':<14}"
        f"{'Count':>8}"
    )

    print("-" * 58)

    rule_statuses = [
        "MATCHED_RULE",
        "HUMAN_REVIEW",
        "NO_MATCH",
    ]

    verification_statuses = [
        "VERIFIED",
        "REJECTED",
        "UNVERIFIED",
    ]

    correctness_statuses = [
        "CORRECT",
        "INCORRECT",
    ]

    for rule_status in rule_statuses:
        for verification_status in (
            verification_statuses
        ):
            for correctness in (
                correctness_statuses
            ):
                count = matrix[
                    (
                        rule_status,
                        verification_status,
                        correctness,
                    )
                ]

                if count == 0:
                    continue

                print(
                    f"{rule_status:<18}"
                    f"{verification_status:<15}"
                    f"{correctness:<14}"
                    f"{count:>8}"
                )

    print()

    # -------------------------------------------------------------
    # Most important recovery category:
    #
    # Rules could not confidently match, but the LLM proposal
    # passed deterministic verification and was correct.
    # -------------------------------------------------------------

    recovered_cases = 0

    for rule_status in (
        "NO_MATCH",
        "HUMAN_REVIEW",
    ):
        recovered_cases += matrix[
            (
                rule_status,
                "VERIFIED",
                "CORRECT",
            )
        ]

    print("Potential Hybrid Recoveries")
    print("---------------------------")
    print(
        f"Rules uncertain + verifier VERIFIED "
        f"+ ground truth correct : "
        f"{recovered_cases}"
    )

    print()

    print("Potential False Accepts")
    print("-----------------------")

    false_accepts = 0

    for rule_status in (
        "NO_MATCH",
        "HUMAN_REVIEW",
    ):
        false_accepts += matrix[
            (
                rule_status,
                "VERIFIED",
                "INCORRECT",
            )
        ]

    print(
        f"Rules uncertain + verifier VERIFIED "
        f"+ ground truth incorrect : "
        f"{false_accepts}"
    )

    print()

    print("Examples")
    print("--------")

    interesting_keys = [
        (
            "NO_MATCH",
            "VERIFIED",
            "CORRECT",
        ),
        (
            "HUMAN_REVIEW",
            "VERIFIED",
            "CORRECT",
        ),
        (
            "NO_MATCH",
            "VERIFIED",
            "INCORRECT",
        ),
        (
            "HUMAN_REVIEW",
            "VERIFIED",
            "INCORRECT",
        ),
    ]

    for key in interesting_keys:
        ids = examples.get(key, [])

        if not ids:
            continue

        print(
            f"{key[0]} + "
            f"{key[1]} + "
            f"{key[2]}"
        )

        for settlement_id in ids:
            print(
                f"  {settlement_id}"
            )

if __name__ == "__main__":
    main()