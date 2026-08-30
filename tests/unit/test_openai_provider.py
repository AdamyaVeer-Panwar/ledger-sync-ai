import pytest

from openai import APIConnectionError, APITimeoutError

from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
)
from app.infrastructure.llm.openai_provider import OpenAIResolver


class FakeParsed:
    def model_dump(self):
        return {
            "decision": "MATCH",
            "candidate_ids": ["L001"],
            "confidence": 0.94,
            "evidence_codes": [
                "EXACT_AMOUNT",
                "SAME_MERCHANT",
            ],
        }


class FakeContent:
    type = "output_text"
    parsed = FakeParsed()


class FakeOutput:
    type = "message"
    content = [FakeContent()]


class FakeUsage:
    input_tokens = 100
    output_tokens = 20
    total_tokens = 120


class FakeResponse:
    output = [FakeOutput()]
    usage = FakeUsage()


class FakeResponses:
    async def parse(self, **kwargs):
        assert kwargs["model"] == "test-model"
        assert kwargs["text_format"] is AIResolution

        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


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


@pytest.mark.asyncio
async def test_provider_returns_valid_ai_resolution():
    resolver = OpenAIResolver.__new__(OpenAIResolver)

    resolver.client = FakeClient()
    resolver.model = "test-model"
    resolver.prompt = "test prompt"

    result = await resolver.resolve(
        make_settlement(),
        [make_ledger()],
    )

    assert result.resolution.decision == (
        AIResolutionDecision.MATCH
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
async def test_provider_raises_when_no_structured_output():
    class EmptyResponses:
        async def parse(self, **kwargs):
            class EmptyResponse:
                output = []

            return EmptyResponse()

    class EmptyClient:
        responses = EmptyResponses()

    resolver = OpenAIResolver.__new__(OpenAIResolver)

    resolver.client = EmptyClient()
    resolver.model = "test-model"
    resolver.prompt = "test prompt"

    with pytest.raises(
        LLMProviderError,
        match="LLM returned no valid structured AIResolution",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


def test_provider_loads_prompt():
    resolver = OpenAIResolver(
        api_key="test-key",
        model="test-model",
        prompt_path="prompts/reconciliation_v1.txt",
    )

    assert resolver.prompt
    assert (
        "financial reconciliation resolver"
        in resolver.prompt
    )


@pytest.mark.asyncio
async def test_provider_translates_timeout_error():
    class TimeoutResponses:
        async def parse(self, **kwargs):
            raise APITimeoutError(request=None)

    class TimeoutClient:
        responses = TimeoutResponses()

    resolver = OpenAIResolver.__new__(OpenAIResolver)

    resolver.client = TimeoutClient()
    resolver.model = "test-model"
    resolver.prompt = "test prompt"

    with pytest.raises(
        LLMTimeoutError,
        match="LLM request timed out",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )


@pytest.mark.asyncio
async def test_provider_translates_connection_error():
    class FailingResponses:
        async def parse(self, **kwargs):
            raise APIConnectionError(request=None)

    class FailingClient:
        responses = FailingResponses()

    resolver = OpenAIResolver.__new__(OpenAIResolver)

    resolver.client = FailingClient()
    resolver.model = "test-model"
    resolver.prompt = "test prompt"

    with pytest.raises(
        LLMProviderError,
        match="LLM provider request failed",
    ):
        await resolver.resolve(
            make_settlement(),
            [make_ledger()],
        )