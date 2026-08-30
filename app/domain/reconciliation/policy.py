from dataclasses import dataclass
from enum import Enum

from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusionResult,
    FusionAgreement,
)


class PolicyAction(str, Enum):
    AUTO_MATCH = "AUTO_MATCH"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    NO_MATCH = "NO_MATCH"


@dataclass(frozen=True)
class PolicyDecision:
    action: PolicyAction
    candidate_ids: list[str]
    confidence: float
    evidence_codes: list[str]
    reason: str


class PolicyEngine:
    def __init__(
        self,
        *,
        high_threshold: float,
        medium_threshold: float,
    ) -> None:
        if not 0.0 <= medium_threshold <= 1.0:
            raise ValueError(
                "medium_threshold must be between 0 and 1"
            )

        if not 0.0 <= high_threshold <= 1.0:
            raise ValueError(
                "high_threshold must be between 0 and 1"
            )

        if medium_threshold > high_threshold:
            raise ValueError(
                "medium_threshold cannot exceed "
                "high_threshold"
            )

        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def evaluate(
        self,
        fusion_result: EvidenceFusionResult,
    ) -> PolicyDecision:

        confidence = fusion_result.confidence

        # ---------------------------------------------------------
        # Conflict is never auto-match.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.CONFLICT
        ):
            return PolicyDecision(
                action=PolicyAction.HUMAN_REVIEW,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason="rules and LLM evidence conflict",
            )

        # ---------------------------------------------------------
        # Strong agreement can be auto-matched when confidence
        # clears the high threshold.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.STRONG_AGREEMENT
            and confidence >= self.high_threshold
        ):
            return PolicyDecision(
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason="strong agreement above high threshold",
            )

        # ---------------------------------------------------------
        # Medium confidence → human review.
        # ---------------------------------------------------------

        if confidence >= self.medium_threshold:
            return PolicyDecision(
                action=PolicyAction.HUMAN_REVIEW,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason="confidence requires human review",
            )

        # ---------------------------------------------------------
        # Low confidence → no match.
        # ---------------------------------------------------------

        return PolicyDecision(
            action=PolicyAction.NO_MATCH,
            candidate_ids=list(
                fusion_result.candidate_ids
            ),
            confidence=confidence,
            evidence_codes=list(
                fusion_result.evidence_codes
            ),
            reason="confidence below medium threshold",
        )