import asyncio

from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.ollama_provider import OllamaResolver


async def main() -> None:
    resolver = OllamaResolver(
        model="qwen2.5:3b",
        timeout=120.0,
    )

    settlement = SettlementRecord(
        settlement_id="OLLAMA-S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date="2026-08-25",
        reference="UTR-001",
    )

    candidate = LedgerRecord(
        ledger_id="OLLAMA-L001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        transaction_date="2026-08-25",
        reference="UTR-001",
        entry_type="PAYMENT",
    )

    result = await resolver.resolve(
        settlement,
        [candidate],
    )

    print("Ollama smoke test successful")
    print(
        f"Decision      : "
        f"{result.resolution.decision}"
    )
    print(
        f"Candidate ID  : "
        f"{result.resolution.candidate_id}"
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