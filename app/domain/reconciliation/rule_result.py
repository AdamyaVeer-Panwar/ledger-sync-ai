from dataclasses import dataclass

from app.domain.enums import MatchStatus
from app.domain.models import MatchDecision


@dataclass(frozen=True)
class RuleMatchResult:
    """
    Normalized deterministic result used by the hybrid resolver.

    This object contains the output of the rule engine in a form
    that can be combined with an LLM resolution.
    """

    status: MatchStatus
    candidate_ids: list[str]
    confidence: float
    evidence_codes: list[str]
    is_confident: bool


def to_rule_match_result(
    decision: MatchDecision,
) -> RuleMatchResult:
    is_confident = (
        decision.status == MatchStatus.MATCHED_RULE
        and len(decision.candidate_ids) == 1
    )

    return RuleMatchResult(
        status=decision.status,
        candidate_ids=list(
            decision.candidate_ids
        ),
        confidence=decision.confidence,
        evidence_codes=list(
            decision.evidence
        ),
        is_confident=is_confident,
    )