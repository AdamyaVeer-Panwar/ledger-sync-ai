import pytest

from app.domain.ai.models import AIResolution
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.base import LLMResolver


def test_llm_resolver_is_abstract():
    with pytest.raises(TypeError):
        LLMResolver()


def test_concrete_resolver_must_implement_resolve():
    class IncompleteResolver(LLMResolver):
        pass

    with pytest.raises(TypeError):
        IncompleteResolver()


def test_concrete_resolver_can_implement_interface():
    class FakeResolver(LLMResolver):
        async def resolve(
            self,
            settlement: SettlementRecord,
            candidates: list[LedgerRecord],
        ) -> AIResolution:
            return AIResolution(
                decision="NO_MATCH",
                confidence=0.0,
                evidence_codes=["TEST"],
            )

    resolver = FakeResolver()

    assert isinstance(resolver, LLMResolver)