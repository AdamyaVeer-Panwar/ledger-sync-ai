from abc import ABC, abstractmethod

from app.domain.ai.models import AIResolution
from app.domain.models import LedgerRecord, SettlementRecord
from app.infrastructure.llm.results import LLMResolutionResult


class LLMResolver(ABC):
    """Provider-independent interface for AI reconciliation."""

    @abstractmethod
    async def resolve(
        self,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> LLMResolutionResult:
        """Resolve a settlement against bounded ledger candidates."""
        raise NotImplementedError

class LLMResolver(ABC):
    """Provider-independent interface for AI reconciliation."""

    @abstractmethod
    async def resolve(
        self,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> LLMResolutionResult:
        """Resolve one settlement against bounded ledger candidates."""
        raise NotImplementedError