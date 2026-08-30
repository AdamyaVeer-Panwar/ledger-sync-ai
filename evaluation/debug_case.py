import asyncio
from decimal import Decimal

from app.db.session import SessionFactory
from app.domain.models import LedgerRecord
from app.infrastructure.llm.ollama_provider import OllamaResolver
from app.repositories.candidate_retriever import CandidateRetriever

from evaluation.benchmark_rules import (
    load_ground_truth,
    load_settlements,
)


async def main():
    settlement = next(
        s
        for s in load_settlements()
        if s.settlement_id == "S000259"
    )

    ground_truth = load_ground_truth()

    expected_ids = ground_truth[
        settlement.settlement_id
    ]

    print("SETTLEMENT")
    print("----------")
    print(
        f"ID        : {settlement.settlement_id}"
    )
    print(
        f"Merchant  : {settlement.merchant_id}"
    )
    print(
        f"Amount    : {settlement.amount}"
    )
    print(
        f"Currency  : {settlement.currency}"
    )
    print(
        f"Date      : {settlement.settlement_date}"
    )
    print(
        f"Reference : {settlement.reference}"
    )

    print()
    print("GROUND TRUTH")
    print("------------")
    print(expected_ids)

    async with SessionFactory() as session:
        retriever = CandidateRetriever(session)

        candidates_orm = await retriever.retrieve(
            merchant_id=settlement.merchant_id,
            currency=settlement.currency,
            amount=settlement.amount,
            transaction_date=settlement.settlement_date,
            reference=settlement.reference,
            amount_tolerance=Decimal("0.02"),
            date_window_days=2,
            limit=50,
        )

        print()
        print("RETRIEVED")
        print("---------")

        if not candidates_orm:
            print("NO CANDIDATES")
            return

        for candidate in candidates_orm:
            print(
                candidate.ledger_id,
                candidate.merchant_id,
                candidate.amount,
                candidate.currency,
                candidate.transaction_date,
                candidate.reference,
            )

        candidates = [
            LedgerRecord(
                ledger_id=candidate.ledger_id,
                merchant_id=candidate.merchant_id,
                amount=candidate.amount,
                currency=candidate.currency,
                transaction_date=candidate.transaction_date,
                reference=candidate.reference,
                entry_type=candidate.entry_type,
            )
            for candidate in candidates_orm
        ]

    print()
    print("OLLAMA RESOLUTION")
    print("-----------------")

    resolver = OllamaResolver(
        model="qwen2.5:3b",
        timeout=120.0,
    )

    result = await resolver.resolve(
        settlement,
        candidates,
    )

    print(
        f"Decision      : "
        f"{result.resolution.decision}"
    )

    print(
        f"Candidate IDs  : "
        f"{result.resolution.candidate_ids}"
    )

    print(
        f"Confidence    : "
        f"{result.resolution.confidence}"
    )

    print(
        f"Evidence      : "
        f"{result.resolution.evidence_codes}"
    )

    print(
        f"Input tokens  : "
        f"{result.usage.input_tokens}"
    )

    print(
        f"Output tokens : "
        f"{result.usage.output_tokens}"
    )

    print(
        f"Total tokens  : "
        f"{result.usage.total_tokens}"
    )


if __name__ == "__main__":
    asyncio.run(main())