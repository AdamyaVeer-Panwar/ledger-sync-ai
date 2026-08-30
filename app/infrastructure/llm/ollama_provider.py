import json
from pathlib import Path

import httpx

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


class OllamaResolver(LLMResolver):
    """Ollama-backed local implementation of LLMResolver."""

    def __init__(
        self,
        *,
        model: str,
        timeout: float = 120.0,
        prompt_path: str = "prompts/reconciliation_v1.txt",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

        self.prompt = Path(prompt_path).read_text(
            encoding="utf-8"
        )

    async def resolve(
        self,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> LLMResolutionResult:
        """Resolve settlement against bounded candidates."""

        payload = {
            "model": self.model,
            "prompt": self._build_input(
                settlement=settlement,
                candidates=candidates,
            ),
            "stream": False,
            "format": AIResolution.model_json_schema(),
            "options": {
                "temperature": 0,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                "Ollama request timed out"
            ) from exc

        except httpx.HTTPError as exc:
            raise LLMProviderError(
                "Ollama provider request failed"
            ) from exc

        try:
            data = response.json()

            raw_response = data["response"]

            parsed = json.loads(raw_response)

            resolution = AIResolution.model_validate(
                parsed
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise LLMProviderError(
                "Ollama returned invalid structured output"
            ) from exc

        prompt_tokens = int(
            data.get("prompt_eval_count", 0)
        )

        output_tokens = int(
            data.get("eval_count", 0)
        )

        total_tokens = (
            prompt_tokens
            + output_tokens
        )

        usage = LLMUsage(
            input_tokens=prompt_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )

        return LLMResolutionResult(
            resolution=resolution,
            usage=usage,
        )

    def _build_input(
        self,
        *,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> str:
        candidate_text = "\n".join(
            (
                f"- candidate_ids: {ledger.ledger_id}\n"
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
            f"- settlement_id: "
            f"{settlement.settlement_id}\n"
            f"- merchant_id: "
            f"{settlement.merchant_id}\n"
            f"- amount: "
            f"{settlement.amount}\n"
            f"- currency: "
            f"{settlement.currency}\n"
            f"- settlement_date: "
            f"{settlement.settlement_date}\n"
            f"- reference: "
            f"{settlement.reference}\n\n"
            "Candidates:\n"
            f"{candidate_text}"
        )