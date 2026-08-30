from dataclasses import dataclass

from app.domain.reconciliation.policy import PolicyAction


@dataclass(frozen=True)
class HybridResolution:
    settlement_id: str
    action: PolicyAction
    candidate_ids: list[str]
    confidence: float
    evidence_codes: list[str]
    reason: str