from pathlib import Path

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
)

from app.domain.ai.models import AIResolution
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.base import LLMResolver
from app.infrastructure.llm.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
)
from app.infrastructure.llm.results import (
    LLMResolutionResult,
    LLMUsage,
)

class OpenAIResolver(LLMResolver):
    """OpenAI-backed implementation of the LLMResolver contract."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout: float = 30.0,
        max_retries: int = 2,
        prompt_path: str = "prompts/reconciliation_v1.txt",
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.model = model

        self.prompt = Path(prompt_path).read_text(
            encoding="utf-8"
        )

    async def resolve(
    self,
    settlement: SettlementRecord,
    candidates: list[LedgerRecord],
) -> LLMResolutionResult:
        """Resolve one settlement against bounded ledger candidates."""

        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=self._build_input(
                    settlement=settlement,
                    candidates=candidates,
                ),
                text_format=AIResolution,
            )

        except APITimeoutError as exc:
            raise LLMTimeoutError(
                "LLM request timed out"
            ) from exc

        except (
            APIConnectionError,
            APIStatusError,
        ) as exc:
            raise LLMProviderError(
                "LLM provider request failed"
            ) from exc

        for output in response.output:
            if output.type != "message":
                continue

            for content in output.content:
                if content.type != "output_text":
                    continue

                if content.parsed is None:
                    continue

                # Explicit Pydantic validation boundary.
                resolution = AIResolution.model_validate(
                    content.parsed.model_dump()
                )

                usage = response.usage

                return LLMResolutionResult(
                    resolution=resolution,
                    usage=LLMUsage(
                        input_tokens=usage.input_tokens,
                        output_tokens=usage.output_tokens,
                        total_tokens=usage.total_tokens,
                    ),
                )

        raise LLMProviderError(
            "LLM returned no valid structured AIResolution"
        )

    def _build_input(
        self,
        *,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> str:
        candidate_text = "\n".join(
            (
                f"- candidate_id: {ledger.ledger_id}\n"
                f"  merchant_id: {ledger.merchant_id}\n"
                f"  amount: {ledger.amount}\n"
                f"  currency: {ledger.currency}\n"
                f"  transaction_date: "
                f"{ledger.transaction_date}\n"
                f"  reference: {ledger.reference}\n"
                f"  entry_type: {ledger.entry_type.value}"
            )
            for ledger in candidates
        )

        return (
            f"{self.prompt}\n\n"
            "Settlement:\n"
            f"- settlement_id: {settlement.settlement_id}\n"
            f"- merchant_id: {settlement.merchant_id}\n"
            f"- amount: {settlement.amount}\n"
            f"- currency: {settlement.currency}\n"
            f"- settlement_date: "
            f"{settlement.settlement_date}\n"
            f"- reference: {settlement.reference}\n\n"
            "Candidates:\n"
            f"{candidate_text}"
        )