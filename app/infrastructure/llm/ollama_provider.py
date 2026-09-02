import json
import time
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
from app.observability.logging import (
    log_llm_invocation,
)
from app.observability.metrics import (
    llm_calls_total,
    llm_failures_total,
    llm_latency_seconds,
)


class OllamaResolver(LLMResolver):
    """
    Ollama-backed implementation of the LLMResolver contract.

    Responsibilities:
        - build the bounded reconciliation prompt
        - call the Ollama provider
        - validate structured model output
        - expose provider-level telemetry

    It does NOT:
        - make reconciliation policy decisions
        - verify whether a proposed match is correct
        - authorize an automatic match

    Prompt contents and model responses are never written to logs.
    """

    def __init__(
        self,
        *,
        model: str,
        timeout: float = 120.0,
        prompt_path: str = (
            "prompts/reconciliation_v1.txt"
        ),
        base_url: str = (
            "http://localhost:11434"
        ),
    ) -> None:
        self.model = model
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

        self.prompt = Path(
            prompt_path
        ).read_text(
            encoding="utf-8"
        )

    async def resolve(
        self,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> LLMResolutionResult:
        """
        Resolve a settlement against a bounded candidate set.

        Every invocation produces:

            - one LLM call counter increment
            - one HTTP latency observation
            - one structured invocation event

        Provider failures are translated into application-specific
        LLM exceptions.
        """

        llm_calls_total.inc()

        invocation_start = time.perf_counter()

        invocation_status = "failure"
        invocation_error_type: str | None = None

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
            # -----------------------------------------------------
            # 1. Call the LLM provider.
            #
            # The HTTP latency metric measures only this operation.
            # -----------------------------------------------------

            http_start = time.perf_counter()

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
                llm_failures_total.inc()

                invocation_error_type = (
                    type(exc).__name__
                )

                raise LLMTimeoutError(
                    "Ollama request timed out"
                ) from exc

            except httpx.HTTPError as exc:
                llm_failures_total.inc()

                invocation_error_type = (
                    type(exc).__name__
                )

                raise LLMProviderError(
                    "Ollama provider request failed"
                ) from exc

            finally:
                # This metric represents provider HTTP latency,
                # including failed HTTP requests.
                llm_latency_seconds.observe(
                    time.perf_counter() - http_start
                )

            # -----------------------------------------------------
            # 2. Parse and validate model output.
            # -----------------------------------------------------

            try:
                data = response.json()

                raw_response = data["response"]

                parsed = json.loads(
                    raw_response
                )

                resolution = (
                    AIResolution.model_validate(
                        parsed
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
            ) as exc:
                llm_failures_total.inc()

                invocation_error_type = (
                    type(exc).__name__
                )

                raise LLMProviderError(
                    "Ollama returned invalid structured output"
                ) from exc

            # -----------------------------------------------------
            # 3. Extract token usage.
            # -----------------------------------------------------

            input_tokens = int(
                data.get(
                    "prompt_eval_count",
                    0,
                )
            )

            output_tokens = int(
                data.get(
                    "eval_count",
                    0,
                )
            )

            total_tokens = (
                input_tokens
                + output_tokens
            )

            usage = LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )

            invocation_status = "success"

            return LLMResolutionResult(
                resolution=resolution,
                usage=usage,
            )

        finally:
            # -----------------------------------------------------
            # 4. Emit one structured event for the whole invocation.
            #
            # This finally executes for:
            #   - successful responses
            #   - provider failures
            #   - timeout failures
            #   - malformed model output
            #
            # Prompt and response content are intentionally omitted.
            # -----------------------------------------------------

            try:
                log_llm_invocation(
                    model=self.model,
                    candidate_count=len(candidates),
                    status=invocation_status,
                    duration_ms=(
                        time.perf_counter()
                        - invocation_start
                    ) * 1000,
                    error_type=invocation_error_type,
                )
            except Exception:
                # Observability must never change provider behavior.
                pass

    def _build_input(
        self,
        *,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> str:
        """
        Build the bounded reconciliation prompt.
        """

        candidate_text = "\n".join(
            (
                f"- candidate_id: "
                f"{ledger.ledger_id}\n"
                f"  merchant_id: "
                f"{ledger.merchant_id}\n"
                f"  amount: "
                f"{ledger.amount}\n"
                f"  currency: "
                f"{ledger.currency}\n"
                f"  transaction_date: "
                f"{ledger.transaction_date}\n"
                f"  reference: "
                f"{ledger.reference}\n"
                f"  entry_type: "
                f"{ledger.entry_type.value}"
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