from dataclasses import dataclass
from enum import Enum


class FusionAgreement(str, Enum):
    STRONG_AGREEMENT = "STRONG_AGREEMENT"
    LLM_SUPPORTED = "LLM_SUPPORTED"
    CONFLICT = "CONFLICT"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class EvidenceFusionResult:
    candidate_ids: list[str]
    agreement: FusionAgreement
    confidence: float
    evidence_codes: list[str]