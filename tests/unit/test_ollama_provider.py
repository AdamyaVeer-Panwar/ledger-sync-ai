import pytest

import httpx

from app.domain.ai.models import AIResolution, AIResolutionDecision
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
)
from app.infrastructure.llm.ollama_provider import OllamaResolver


def make_settlement():
    return SettlementRecord(
        settlement_id="S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date="2026-08-25",
        reference="UTR-001",
    )


def make_ledger():
    return LedgerRecord(
        ledger_id="L001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        transaction_date="2026-08-25",
        reference="UTR-001",
        entry_type="PAYMENT",
    )


class FakeResponse:
    def __init__(
        self,
        *,
        json_data,
        status_code=200,
    ):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(
                f"HTTP {self.status_code}"
            )

    def json(self):
        return self._json_data


class FakeAsyncClient:
    def __init__(
        self,
        *,
        response,
    ):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    async def post(self, *args, **kwargs):
        return self.response


@pytest.mark.asyncio
async def test_ollama_provider_returns_valid_resolution(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"MATCH",'
                '"candidate_ids":["L001"],'
                '"confidence":0.94,'
                '"evidence_codes":'
                '["EXACT_AMOUNT","SAME_MERCHANT"]}'
            ),
            "prompt_eval_count": 100,
            "eval_count": 20,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    result = await resolver.resolve(
        make_settlement(),
        [make_ledger()],
    )

    assert isinstance(
        result.resolution,
        AIResolution,
    )

    assert (
        result.resolution.decision
        == AIResolutionDecision.MATCH
    )

    assert result.resolution.candidate_ids == [
        "L001"
    ]

    assert result.resolution.confidence == 0.94

    assert result.resolution.evidence_codes == [
        "EXACT_AMOUNT",
        "SAME_MERCHANT",
    ]

    assert result.usage.input_tokens == 100
    assert result.usage.output_tokens == 20
    assert result.usage.total_tokens == 120


@pytest.mark.asyncio
async def test_ollama_provider_rejects_invalid_json(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": "this is not json",
            "prompt_eval_count": 100,
            "eval_count": 10,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="invalid structured output",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_translates_timeout(
    monkeypatch,
):
    class TimeoutAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        async def post(self, *args, **kwargs):
            request = httpx.Request(
                "POST",
                "http://localhost:11434/api/generate",
            )

            raise httpx.ReadTimeout(
                "request timed out",
                request=request,
            )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        lambda *args, **kwargs: TimeoutAsyncClient(),
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMTimeoutError,
        match="Ollama request timed out",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_translates_http_error(
    monkeypatch,
):
    class FailingResponse:
        def raise_for_status(self):
            request = httpx.Request(
                "POST",
                "http://localhost:11434/api/generate",
            )

            response = httpx.Response(
                500,
                request=request,
            )

            raise httpx.HTTPStatusError(
                "HTTP 500",
                request=request,
                response=response,
            )

        def json(self):
            return {}

    class FailingAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        async def post(self, *args, **kwargs):
            return FailingResponse()

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        lambda *args, **kwargs: FailingAsyncClient(),
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="Ollama provider request failed",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_supports_multiple_candidate_ids(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"MATCH",'
                '"candidate_ids":["L000297","L000298"],'
                '"confidence":0.94,'
                '"evidence_codes":'
                '["PARTIAL_REFUND"]}'
            ),
            "prompt_eval_count": 120,
            "eval_count": 25,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    result = await resolver.resolve(
        make_settlement(),
        [
            LedgerRecord(
                ledger_id="L000297",
                merchant_id="M009",
                amount="8141.50",
                currency="INR",
                transaction_date="2026-08-22",
                reference="UTR-S000259",
                entry_type="PAYMENT",
            ),
            LedgerRecord(
                ledger_id="L000298",
                merchant_id="M009",
                amount="60.44",
                currency="INR",
                transaction_date="2026-08-23",
                reference="UTR-S000259-REFUND",
                entry_type="REFUND",
            ),
        ],
    )

    assert (
        result.resolution.decision
        == AIResolutionDecision.MATCH
    )

    assert result.resolution.candidate_ids == [
        "L000297",
        "L000298",
    ]

@pytest.mark.asyncio
async def test_ollama_provider_rejects_confidence_outside_range(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"MATCH",'
                '"candidate_ids":["L001"],'
                '"confidence":1.5,'
                '"evidence_codes":[]}'
            ),
            "prompt_eval_count": 100,
            "eval_count": 10,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="invalid structured output",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_rejects_match_without_candidates(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"MATCH",'
                '"candidate_ids":[],'
                '"confidence":0.8,'
                '"evidence_codes":[]}'
            ),
            "prompt_eval_count": 100,
            "eval_count": 10,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="invalid structured output",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_rejects_no_match_with_candidates(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"NO_MATCH",'
                '"candidate_ids":["L001"],'
                '"confidence":0.2,'
                '"evidence_codes":[]}'
            ),
            "prompt_eval_count": 100,
            "eval_count": 10,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="invalid structured output",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_ollama_provider_rejects_malformed_structured_json(
    monkeypatch,
):
    response = FakeResponse(
        json_data={
            "response": (
                '{"decision":"MATCH",'
                '"candidate_ids":["L001"],'
                '"confidence":"very-high",'
                '"evidence_codes":[]}'
            ),
            "prompt_eval_count": 100,
            "eval_count": 10,
        }
    )

    def fake_client(*args, **kwargs):
        return FakeAsyncClient(
            response=response,
        )

    monkeypatch.setattr(
        "app.infrastructure.llm.ollama_provider.httpx.AsyncClient",
        fake_client,
    )

    resolver = OllamaResolver(
        model="qwen2.5:3b",
    )

    with pytest.raises(
        LLMProviderError,
        match="invalid structured output",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )