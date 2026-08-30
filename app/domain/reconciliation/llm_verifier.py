from dataclasses import dataclass
from decimal import Decimal

from app.domain.ai.models import AIResolution, AIResolutionDecision
from app.domain.models import LedgerRecord, SettlementRecord


from enum import Enum


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"

@dataclass(frozen=True)
class LLMVerificationResult:
    status: str
    candidate_ids: list[str]
    evidence_codes: list[str]
    reason: str


class LLMVerifier:
    """
    Deterministically validates an LLM reconciliation proposal.

    The verifier does not call an LLM and does not make a final
    authorization decision. It checks whether the proposed
    candidate set is supported by deterministic evidence.
    """

    def verify(
        self,
        *,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
        resolution: AIResolution,
    ) -> LLMVerificationResult:

        candidate_map = {
            ledger.ledger_id: ledger
            for ledger in candidates
        }

        proposed_ids = list(
            resolution.candidate_ids
        )

        # ---------------------------------------------------------
        # NO_MATCH
        # ---------------------------------------------------------

        if (
            resolution.decision
            == AIResolutionDecision.NO_MATCH
        ):
            if proposed_ids:
                return LLMVerificationResult(
                    status=VerificationStatus.REJECTED,
                    candidate_ids=proposed_ids,
                    evidence_codes=[
                        "no_match_with_candidates"
                    ],
                    reason=(
                        "NO_MATCH must not contain "
                        "candidate IDs"
                    ),
                )

            return LLMVerificationResult(
                status=VerificationStatus.VERIFIED,
                candidate_ids=[],
                evidence_codes=[
                    "no_match"
                ],
                reason="LLM proposed no match",
            )

        # ---------------------------------------------------------
        # MATCH / AMBIGUOUS requires candidate IDs.
        # ---------------------------------------------------------

        if not proposed_ids:
            return LLMVerificationResult(
                status=VerificationStatus.REJECTED,
                candidate_ids=[],
                evidence_codes=[
                    "missing_candidate_ids"
                ],
                reason=(
                    "resolution requires candidate IDs"
                ),
            )

        # ---------------------------------------------------------
        # Candidate existence
        # ---------------------------------------------------------

        missing_ids = [
            candidate_id
            for candidate_id in proposed_ids
            if candidate_id not in candidate_map
        ]

        if missing_ids:
            return LLMVerificationResult(
                status=VerificationStatus.REJECTED,
                candidate_ids=proposed_ids,
                evidence_codes=[
                    "candidate_not_retrieved"
                ],
                reason=(
                    "LLM proposed candidate IDs that "
                    "were not retrieved"
                ),
            )

        selected = [
            candidate_map[candidate_id]
            for candidate_id in proposed_ids
        ]

        # ---------------------------------------------------------
        # Candidate invariants
        # ---------------------------------------------------------

        for ledger in selected:

            if ledger.merchant_id != settlement.merchant_id:
                return LLMVerificationResult(
                    status=VerificationStatus.REJECTED,
                    candidate_ids=proposed_ids,
                    evidence_codes=[
                        "merchant_mismatch"
                    ],
                    reason=(
                        "candidate merchant does not "
                        "match settlement merchant"
                    ),
                )

            if ledger.currency != settlement.currency:
                return LLMVerificationResult(
                    status=VerificationStatus.REJECTED,
                    candidate_ids=proposed_ids,
                    evidence_codes=[
                        "currency_mismatch"
                    ],
                    reason=(
                        "candidate currency does not "
                        "match settlement currency"
                    ),
                )

        # ---------------------------------------------------------
        # Explicit ambiguity is valid but not deterministic proof.
        # ---------------------------------------------------------

        if (
            resolution.decision
            == AIResolutionDecision.AMBIGUOUS
        ):
            return LLMVerificationResult(
                status=VerificationStatus.UNVERIFIED,
                candidate_ids=proposed_ids,
                evidence_codes=[
                    "ambiguous_candidate_set"
                ],
                reason=(
                    "multiple plausible candidates "
                    "remain unresolved"
                ),
            )

        # ---------------------------------------------------------
        # SINGLE-CANDIDATE MATCH
        # ---------------------------------------------------------

        if len(selected) == 1:

            ledger = selected[0]

            if ledger.amount != settlement.amount:
                return LLMVerificationResult(
                    status=VerificationStatus.REJECTED,
                    candidate_ids=proposed_ids,
                    evidence_codes=[
                        "amount_mismatch"
                    ],
                    reason=(
                        "single candidate amount does "
                        "not equal settlement amount"
                    ),
                )

            return LLMVerificationResult(
                status=VerificationStatus.VERIFIED,
                candidate_ids=proposed_ids,
                evidence_codes=[
                    "candidate_ids_valid",
                    "merchant_verified",
                    "currency_verified",
                    "amount_verified",
                ],
                reason=(
                    "single candidate exactly "
                    "reconciles settlement"
                ),
            )

        # ---------------------------------------------------------
        # MULTI-CANDIDATE MATCH
        #
        # First attempt the common PAYMENT - REFUND model.
        # ---------------------------------------------------------

        payment_total = sum(
            (
                ledger.amount
                for ledger in selected
                if ledger.entry_type.value == "PAYMENT"
            ),
            Decimal("0"),
        )

        refund_total = sum(
            (
                ledger.amount
                for ledger in selected
                if ledger.entry_type.value == "REFUND"
            ),
            Decimal("0"),
        )

        net_amount = (
            payment_total - refund_total
        )

        if net_amount == settlement.amount:
            return LLMVerificationResult(
                status=VerificationStatus.VERIFIED,
                candidate_ids=proposed_ids,
                evidence_codes=[
                    "candidate_ids_valid",
                    "merchant_verified",
                    "currency_verified",
                    "multi_ledger_arithmetic_verified",
                ],
                reason=(
                    "payment/refund candidate set "
                    "exactly reconciles settlement"
                ),
            )

        # ---------------------------------------------------------
        # Generic positive-sum case.
        #
        # Useful for settlements composed of several positive
        # ledger entries.
        # ---------------------------------------------------------

        positive_total = sum(
            (
                ledger.amount
                for ledger in selected
                if ledger.entry_type.value != "REFUND"
            ),
            Decimal("0"),
        )

        if positive_total == settlement.amount:
            return LLMVerificationResult(
                status=VerificationStatus.VERIFIED,
                candidate_ids=proposed_ids,
                evidence_codes=[
                    "candidate_ids_valid",
                    "merchant_verified",
                    "currency_verified",
                    "multi_ledger_arithmetic_verified",
                ],
                reason=(
                    "candidate amounts exactly "
                    "sum to settlement"
                ),
            )

        # ---------------------------------------------------------
        # We cannot deterministically validate the relationship.
        # Do not assume the LLM is correct.
        # ---------------------------------------------------------

        return LLMVerificationResult(
            status=VerificationStatus.UNVERIFIED,
            candidate_ids=proposed_ids,
            evidence_codes=[
                "multi_ledger_relationship_unverified"
            ],
            reason=(
                "candidate set is valid but its "
                "reconciliation relationship could "
                "not be deterministically verified"
            ),
        )