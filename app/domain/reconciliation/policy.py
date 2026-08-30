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
    """
    Deterministic authorization layer for reconciliation decisions.

    The policy does not trust raw LLM confidence as authorization.
    It evaluates the evidence state produced by EvidenceFusion.

    Policy:

        STRONG_AGREEMENT
            -> AUTO_MATCH

        LLM_SUPPORTED
            -> AUTO_MATCH

        AMBIGUOUS
            -> HUMAN_REVIEW

        CONFLICT
            -> HUMAN_REVIEW

        No candidates / no trustworthy evidence
            -> NO_MATCH
    """

    def evaluate(
        self,
        fusion_result: EvidenceFusionResult,
    ) -> PolicyDecision:

        # ---------------------------------------------------------
        # Strong deterministic + AI agreement.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.STRONG_AGREEMENT
        ):
            return PolicyDecision(
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=fusion_result.confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason=(
                    "deterministic and AI evidence "
                    "strongly agree"
                ),
            )

        # ---------------------------------------------------------
        # LLM-supported result.
        #
        # This state is only produced when the LLM proposal has
        # already passed deterministic verification.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.LLM_SUPPORTED
        ):
            return PolicyDecision(
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=fusion_result.confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason=(
                    "LLM proposal passed deterministic "
                    "verification"
                ),
            )

        # ---------------------------------------------------------
        # Explicit ambiguity.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.AMBIGUOUS
        ):
            return PolicyDecision(
                action=PolicyAction.HUMAN_REVIEW,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=fusion_result.confidence,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason=(
                    "multiple plausible candidates "
                    "remain unresolved"
                ),
            )

        # ---------------------------------------------------------
        # Conflict.
        #
        # Never auto-match a disagreement or failed verification.
        # ---------------------------------------------------------

        if (
            fusion_result.agreement
            == FusionAgreement.CONFLICT
        ):
            if not fusion_result.candidate_ids:
                return PolicyDecision(
                    action=PolicyAction.NO_MATCH,
                    candidate_ids=[],
                    confidence=0.0,
                    evidence_codes=list(
                        fusion_result.evidence_codes
                    ),
                    reason=(
                        "no trustworthy reconciliation "
                        "candidate was established"
                    ),
                )

            return PolicyDecision(
                action=PolicyAction.HUMAN_REVIEW,
                candidate_ids=list(
                    fusion_result.candidate_ids
                ),
                confidence=0.0,
                evidence_codes=list(
                    fusion_result.evidence_codes
                ),
                reason=(
                    "reconciliation evidence conflicts "
                    "or could not be verified"
                ),
            )

        # ---------------------------------------------------------
        # Defensive fallback.
        # ---------------------------------------------------------

        return PolicyDecision(
            action=PolicyAction.HUMAN_REVIEW,
            candidate_ids=list(
                fusion_result.candidate_ids
            ),
            confidence=fusion_result.confidence,
            evidence_codes=list(
                fusion_result.evidence_codes
            ),
            reason="unrecognized fusion state",
        )