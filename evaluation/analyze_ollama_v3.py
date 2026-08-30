import json
from pathlib import Path


RESULTS_FILE = Path(
    "evaluation/results/ollama_baseline_results_v3.jsonl"
)


def main():
    false_matches = []

    with RESULTS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if not line.strip():
                continue

            result = json.loads(line)

            if (
                result["decision"] == "MATCH"
                and result["expected"] is None
            ):
                false_matches.append(result)

    print(
        f"False matches: {len(false_matches)}"
    )

    print()

    for result in false_matches[:20]:
        print(
            result["settlement_id"],
            "| candidates:",
            result["candidate_ids"],
            "| confidence:",
            result["confidence"],
        )


if __name__ == "__main__":
    main()