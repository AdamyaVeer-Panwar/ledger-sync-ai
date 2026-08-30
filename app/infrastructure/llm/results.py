from dataclasses import dataclass

from app.domain.ai.models import AIResolution


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class LLMResolutionResult:
    resolution: AIResolution
    usage: LLMUsage