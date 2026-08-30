import asyncio
import os

from dotenv import load_dotenv

from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.ai.models import AIResolution
from app.infrastructure.llm.openai_provider import OpenAIResolver

load_dotenv()


async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    if not model:
        raise RuntimeError("OPENAI_MODEL is not configured")

    resolver = OpenAIResolver(
        api_key=api_key,
        model=model,
    )

    settlement = SettlementRecord(
        settlement_id="SMOKE-S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date="2026-08-25",
        reference="UTR-001",
    )

    candidate = LedgerRecord(
        ledger_id="SMOKE-L001",
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

    print("LLM smoke test successful")
    print(f"Decision      : {result.resolution.decision}")
    print(f"Candidate ID  : {result.resolution.candidate_id}")
    print(f"Confidence    : {result.resolution.confidence}")
    print(f"Evidence      : {result.resolution.evidence_codes}")
    print(f"Input tokens  : {result.usage.input_tokens}")
    print(f"Output tokens : {result.usage.output_tokens}")
    print(f"Total tokens  : {result.usage.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())