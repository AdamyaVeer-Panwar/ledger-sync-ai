from decimal import Decimal

from app.domain.enums import MatchStatus
from app.domain.models import (
    LedgerRecord,
    MatchDecision,
    SettlementRecord,
)
from app.domain.reconciliation.normalizer import normalize_reference


class RuleMatcher:
    """Pure deterministic reconciliation rule engine.

    The matcher contains business decision logic only.

    It must not:
    - access the database
    - make HTTP calls
    - call an LLM
    - depend on FastAPI
    - mutate input records
    """

    AMOUNT_TOLERANCE = Decimal("0.02")
    DATE_WINDOW_DAYS = 2

    def match(
        self,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
    ) -> MatchDecision:
        """Match one settlement against a bounded candidate set."""

        if not candidates:
            return self._no_match(
                settlement,
                source="rule_matcher",
                evidence=["no_candidates"],
            )

        # ---------------------------------------------------------
        # Rule 1:
        # Exact reference + exact amount + same merchant
        # ---------------------------------------------------------
        exact_reference_matches = [
            ledger
            for ledger in candidates
            if (
                settlement.reference is not None
                and ledger.reference is not None
                and settlement.reference == ledger.reference
                and settlement.amount == ledger.amount
                and settlement.merchant_id == ledger.merchant_id
            )
        ]

        decision = self._resolve_single_candidate(
            settlement=settlement,
            candidates=exact_reference_matches,
            confidence=1.0,
            source="rule_exact_reference_amount",
            evidence=[
                "reference_exact",
                "amount_exact",
            ],
        )

        if decision is not None:
            return decision

        # ---------------------------------------------------------
        # Rule 2:
        # Exact amount + same merchant + same date
        # ---------------------------------------------------------
        same_day_matches = [
            ledger
            for ledger in candidates
            if (
                ledger.merchant_id == settlement.merchant_id
                and ledger.amount == settlement.amount
                and ledger.transaction_date == settlement.settlement_date
            )
        ]

        decision = self._resolve_single_candidate(
            settlement=settlement,
            candidates=same_day_matches,
            confidence=0.95,
            source="rule_exact_amount_merchant_date",
            evidence=[
                "amount_exact",
                "merchant_exact",
                "date_exact",
            ],
        )

        if decision is not None:
            return decision

        # ---------------------------------------------------------
        # Rule 3:
        # Amount tolerance + merchant + date window
        # ---------------------------------------------------------
        tolerance_matches = [
            ledger
            for ledger in candidates
            if (
                ledger.merchant_id == settlement.merchant_id
                and abs(ledger.amount - settlement.amount)
                <= self.AMOUNT_TOLERANCE
                and abs(
                    ledger.transaction_date
                    - settlement.settlement_date
                ).days
                <= self.DATE_WINDOW_DAYS
            )
        ]

        decision = self._resolve_single_candidate(
            settlement=settlement,
            candidates=tolerance_matches,
            confidence=0.85,
            source="rule_amount_tolerance_date_window",
            evidence=[
                "amount_within_tolerance",
                "merchant_exact",
                "date_within_window",
            ],
        )

        if decision is not None:
            return decision

        # ---------------------------------------------------------
        # Rule 4:
        # Known reference normalization + exact amount + same merchant
        # ---------------------------------------------------------
        normalized_settlement_reference = normalize_reference(
            settlement.reference
        )

        normalized_reference_matches = [
            ledger
            for ledger in candidates
            if (
                normalized_settlement_reference is not None
                and normalize_reference(ledger.reference)
                == normalized_settlement_reference
                and ledger.amount == settlement.amount
                and ledger.merchant_id == settlement.merchant_id
            )
        ]

        decision = self._resolve_single_candidate(
            settlement=settlement,
            candidates=normalized_reference_matches,
            confidence=0.90,
            source="rule_normalized_reference_amount",
            evidence=[
                "reference_normalized",
                "amount_exact",
            ],
        )

        if decision is not None:
            return decision

        # No rule produced a deterministic match.
        return self._no_match(
            settlement,
            source="rule_matcher",
            evidence=["no_match"],
        )

    @staticmethod
    def _resolve_single_candidate(
        *,
        settlement: SettlementRecord,
        candidates: list[LedgerRecord],
        confidence: float,
        source: str,
        evidence: list[str],
    ) -> MatchDecision | None:
        """Resolve zero, one, or multiple candidates.

        Exactly one candidate:
            deterministic rule match.

        Multiple candidates:
            ambiguous → human review.

        Zero candidates:
            rule did not match → continue to next rule.
        """

        if len(candidates) == 1:
            ledger = candidates[0]

            return MatchDecision(
                settlement_id=settlement.settlement_id,
                status=MatchStatus.MATCHED_RULE,
                ledger_id=ledger.ledger_id,
                confidence=confidence,
                evidence=evidence,
                source=source,
            )

        if len(candidates) > 1:
            return MatchDecision(
                settlement_id=settlement.settlement_id,
                status=MatchStatus.HUMAN_REVIEW,
                ledger_id=None,
                confidence=0.0,
                evidence=evidence + ["multiple_candidates"],
                source=source,
            )

        return None

    @staticmethod
    def _no_match(
        settlement: SettlementRecord,
        *,
        source: str,
        evidence: list[str],
    ) -> MatchDecision:
        """Create a terminal NO_MATCH decision."""

        return MatchDecision(
            settlement_id=settlement.settlement_id,
            status=MatchStatus.NO_MATCH,
            ledger_id=None,
            confidence=0.0,
            evidence=evidence,
            source=source,
        )