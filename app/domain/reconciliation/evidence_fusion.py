from dataclasses import dataclass
from enum import Enum

from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerificationResult,
    VerificationStatus,
)
from app.domain.reconciliation.rule_result import (
    RuleMatchResult,
)


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


class EvidenceFusion:
    def fuse(
        self,
        rule_result: RuleMatchResult,
        ai_result: AIResolution,
        verification_result: LLMVerificationResult,
    ) -> EvidenceFusionResult:
        rule_ids = set(rule_result.candidate_ids)
        ai_ids = set(ai_result.candidate_ids)

        evidence_codes = (
            list(rule_result.evidence_codes)
            + list(ai_result.evidence_codes)
            + list(verification_result.evidence_codes)
        )

        # ---------------------------------------------------------
        # 1. LLM proposal was deterministically rejected.
        #
        # This has highest precedence because the verifier has
        # established that the AI proposal is not trustworthy.
        # ---------------------------------------------------------

        if (
            verification_result.status
            == VerificationStatus.REJECTED
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    verification_result.candidate_ids
                ),
                agreement=FusionAgreement.CONFLICT,
                confidence=0.0,
                evidence_codes=(
                    evidence_codes
                    + ["llm_verification_rejected"]
                ),
            )

        # ---------------------------------------------------------
        # 2. Deterministic ambiguity is authoritative.
        #
        # If deterministic rules found multiple candidates,
        # the LLM must not arbitrarily collapse that candidate
        # set to a single auto-match.
        #
        # This protects against:
        #
        #   rule -> L001 + L002
        #   llm  -> L001
        #   policy -> AUTO_MATCH
        #
        # which would be unsafe.
        # ---------------------------------------------------------

        if (
            rule_result.status.value == "HUMAN_REVIEW"
            and len(rule_ids) > 1
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    rule_result.candidate_ids
                ),
                agreement=FusionAgreement.AMBIGUOUS,
                confidence=0.0,
                evidence_codes=(
                    evidence_codes
                    + ["deterministic_ambiguity"]
                ),
            )

        # ---------------------------------------------------------
        # 3. LLM explicitly reports ambiguity.
        # ---------------------------------------------------------

        if (
            ai_result.decision
            == AIResolutionDecision.AMBIGUOUS
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    ai_result.candidate_ids
                ),
                agreement=FusionAgreement.AMBIGUOUS,
                confidence=ai_result.confidence,
                evidence_codes=evidence_codes,
            )

        # ---------------------------------------------------------
        # 4. Strong agreement:
        #
        # Rules and LLM selected the same candidates and the
        # LLM proposal passed deterministic verification.
        # ---------------------------------------------------------

        if (
            rule_result.status.value == "MATCHED_RULE"
            and ai_result.decision
            == AIResolutionDecision.MATCH
            and verification_result.status
            == VerificationStatus.VERIFIED
            and rule_ids == ai_ids
            and rule_ids
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    rule_result.candidate_ids
                ),
                agreement=FusionAgreement.STRONG_AGREEMENT,
                confidence=max(
                    rule_result.confidence,
                    ai_result.confidence,
                ),
                evidence_codes=evidence_codes,
            )

        # ---------------------------------------------------------
        # 5. LLM-supported:
        #
        # Deterministic rules were insufficient, but the LLM
        # proposed a candidate set that passed verification.
        # ---------------------------------------------------------

        if (
            not rule_result.is_confident
            and ai_result.decision
            == AIResolutionDecision.MATCH
            and verification_result.status
            == VerificationStatus.VERIFIED
            and ai_ids
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    ai_result.candidate_ids
                ),
                agreement=FusionAgreement.LLM_SUPPORTED,
                confidence=ai_result.confidence,
                evidence_codes=evidence_codes,
            )

        # ---------------------------------------------------------
        # 6. Verified LLM result without a compatible rule result.
        # ---------------------------------------------------------

        if (
            ai_result.decision
            == AIResolutionDecision.MATCH
            and verification_result.status
            == VerificationStatus.VERIFIED
            and ai_ids
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    ai_result.candidate_ids
                ),
                agreement=FusionAgreement.LLM_SUPPORTED,
                confidence=ai_result.confidence,
                evidence_codes=evidence_codes,
            )

        # ---------------------------------------------------------
        # 7. LLM MATCH could not be deterministically verified.
        # ---------------------------------------------------------

        if (
            ai_result.decision
            == AIResolutionDecision.MATCH
            and verification_result.status
            == VerificationStatus.UNVERIFIED
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    ai_result.candidate_ids
                ),
                agreement=FusionAgreement.CONFLICT,
                confidence=0.0,
                evidence_codes=(
                    evidence_codes
                    + ["llm_verification_unverified"]
                ),
            )

        # ---------------------------------------------------------
        # 8. Explicit rules/LLM candidate disagreement.
        # ---------------------------------------------------------

        if (
            rule_ids
            and ai_ids
            and rule_ids != ai_ids
        ):
            return EvidenceFusionResult(
                candidate_ids=list(
                    ai_result.candidate_ids
                ),
                agreement=FusionAgreement.CONFLICT,
                confidence=0.0,
                evidence_codes=(
                    evidence_codes
                    + ["rules_llm_disagreement"]
                ),
            )

        # ---------------------------------------------------------
        # 9. Default:
        #
        # No trustworthy agreement was established.
        # ---------------------------------------------------------

        return EvidenceFusionResult(
            candidate_ids=list(
                ai_result.candidate_ids
            ),
            agreement=FusionAgreement.CONFLICT,
            confidence=0.0,
            evidence_codes=evidence_codes,
        )