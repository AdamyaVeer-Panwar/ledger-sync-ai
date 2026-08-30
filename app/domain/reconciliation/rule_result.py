from dataclasses import dataclass

from app.domain.enums import MatchStatus
from app.domain.models import MatchDecision

@dataclass(frozen=True)
class RuleMatchResult:
    """
    Deterministic assessment produced by the rule engine.

    This is a domain result used by the hybrid resolver.
    It does not perform any matching itself.
    """

    status: MatchStatus

    candidate_ids: list[str]

    confidence: float

    evidence_codes: list[str]

    is_confident: bool


def to_rule_match_result(
    decision: MatchDecision,
) -> RuleMatchResult:
    candidate_ids = (
        [decision.ledger_id]
        if decision.ledger_id is not None
        else []
    )

    is_confident = (
        decision.status == MatchStatus.MATCHED_RULE
        and decision.ledger_id is not None
        and decision.confidence > 0.0
    )

    return RuleMatchResult(
        status=decision.status,
        candidate_ids=candidate_ids,
        confidence=decision.confidence,
        evidence_codes=decision.evidence,
        is_confident=is_confident,
    )