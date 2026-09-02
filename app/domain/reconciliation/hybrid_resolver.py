from decimal import Decimal

from app.domain.enums import MatchStatus
from app.domain.models import (
    LedgerRecord,
    SettlementRecord,
)
from app.domain.reconciliation.evidence_fusion import (
    EvidenceFusion,
)
from app.domain.reconciliation.hybrid_result import (
    HybridResolution,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerifier,
)
from app.domain.reconciliation.policy import (
    PolicyAction,
    PolicyEngine,
)
from app.domain.reconciliation.rule_matcher import (
    RuleMatcher,
)
from app.domain.reconciliation.rule_result import (
    to_rule_match_result,
)
from app.observability.logging import (
    log_evidence_fusion,
    log_llm_verification,
    log_policy_decision,
    log_rule_evaluation,
)


class HybridResolver:
    """
    Orchestrates deterministic reconciliation and bounded AI reasoning.

    Flow:

        Settlement
            ↓
        Candidate Retrieval
            ↓
        Rule Matcher
            ↓
        deterministic decision?
          ├── confident
          │      ↓
          │   AUTO_MATCH
          │
          ├── deterministic ambiguity
          │      ↓
          │   HUMAN_REVIEW
          │      ↓
          │   no LLM call
          │
          └── insufficient evidence
                 ↓
                LLM
                 ↓
          LLM Verification
                 ↓
          Evidence Fusion
                 ↓
           Policy Engine
                 ↓
          HybridResolution

    Design principle:

        The LLM is only used when deterministic reconciliation
        cannot safely establish the outcome.

        If deterministic rules already establish ambiguity,
        the system does not ask the LLM to arbitrarily select
        one candidate.
    """

    def __init__(
        self,
        *,
        rule_matcher: RuleMatcher,
        candidate_retriever,
        llm_resolver,
        verifier: LLMVerifier,
        fusion: EvidenceFusion,
        policy: PolicyEngine,
    ) -> None:
        self.rule_matcher = rule_matcher
        self.candidate_retriever = candidate_retriever
        self.llm_resolver = llm_resolver
        self.verifier = verifier
        self.fusion = fusion
        self.policy = policy

    async def resolve(
        self,
        settlement: SettlementRecord,
    ) -> HybridResolution:
        # ---------------------------------------------------------
        # 1. Retrieve bounded candidates.
        # ---------------------------------------------------------

        orm_candidates = (
            await self.candidate_retriever.retrieve(
                merchant_id=settlement.merchant_id,
                currency=settlement.currency,
                amount=settlement.amount,
                transaction_date=settlement.settlement_date,
                reference=settlement.reference,
                amount_tolerance=Decimal("0.02"),
                date_window_days=2,
                limit=50,
            )
        )

        candidates = [
            self._to_domain_ledger(ledger)
            for ledger in orm_candidates
        ]

        # ---------------------------------------------------------
        # 2. Run deterministic reconciliation rules.
        # ---------------------------------------------------------

        rule_decision = self.rule_matcher.match(
            settlement=settlement,
            candidates=candidates,
        )

        rule_result = to_rule_match_result(
            rule_decision
        )

        # ---------------------------------------------------------
        # 2a. Emit rule-stage telemetry.
        #
        # Logging must never affect reconciliation correctness.
        # ---------------------------------------------------------

        try:
            log_rule_evaluation(
                decision=rule_result.status.value,
                confidence=rule_result.confidence,
                candidate_count=len(
                    rule_result.candidate_ids
                ),
            )
        except Exception:
            pass

        # ---------------------------------------------------------
        # 3. Strong deterministic result.
        #
        # Deterministic evidence is sufficient.
        # The LLM is not invoked.
        # ---------------------------------------------------------

        if rule_result.is_confident:
            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.AUTO_MATCH,
                candidate_ids=list(
                    rule_result.candidate_ids
                ),
                confidence=rule_result.confidence,
                evidence_codes=list(
                    rule_result.evidence_codes
                ),
                reason=(
                    "confident deterministic rule match"
                ),
                llm_invoked=False,
            )

        # ---------------------------------------------------------
        # 4. Deterministic ambiguity short-circuit.
        #
        # Multiple equally plausible candidates cannot be safely
        # distinguished by the existing deterministic evidence.
        #
        # Do not ask the LLM to arbitrarily choose one.
        # ---------------------------------------------------------

        if (
            rule_result.status
            == MatchStatus.HUMAN_REVIEW
            and "multiple_candidates"
            in rule_result.evidence_codes
        ):
            return HybridResolution(
                settlement_id=settlement.settlement_id,
                action=PolicyAction.HUMAN_REVIEW,
                candidate_ids=list(
                    rule_result.candidate_ids
                ),
                confidence=0.0,
                evidence_codes=list(
                    rule_result.evidence_codes
                ),
                reason=(
                    "deterministic ambiguity requires "
                    "human review"
                ),
                llm_invoked=False,
            )

        # ---------------------------------------------------------
        # 5. Rules are insufficient.
        #
        # This is the ONLY point where the LLM is invoked.
        # ---------------------------------------------------------

        ai_result = await self.llm_resolver.resolve(
            settlement,
            candidates,
        )

        # ---------------------------------------------------------
        # 6. Deterministically verify the LLM proposal.
        #
        # The LLM proposes.
        # The verifier determines whether the proposal has
        # objective support.
        # ---------------------------------------------------------

        verification_result = self.verifier.verify(
            settlement=settlement,
            candidates=candidates,
            resolution=ai_result.resolution,
        )

        try:
            log_llm_verification(
                status=verification_result.status,
                candidate_count=len(
                    verification_result.candidate_ids
                ),
                reason=verification_result.reason,
            )
        except Exception:
            pass

        # ---------------------------------------------------------
        # 7. Fuse rule evidence + AI evidence + verification.
        # ---------------------------------------------------------

        fusion_result = self.fusion.fuse(
            rule_result,
            ai_result.resolution,
            verification_result,
        )

        try:
            log_evidence_fusion(
                agreement=fusion_result.agreement.value,
                candidate_count=len(
                    fusion_result.candidate_ids
                ),
                confidence=fusion_result.confidence,
            )
        except Exception:
            pass

        # ---------------------------------------------------------
        # 8. Policy is the final authorization boundary.
        # ---------------------------------------------------------

        policy_decision = self.policy.evaluate(
            fusion_result
        )

        try:
            log_policy_decision(
                action=policy_decision.action.value,
                candidate_count=len(
                    policy_decision.candidate_ids
                ),
                confidence=policy_decision.confidence,
                reason=policy_decision.reason,
            )
        except Exception:
            pass

        # ---------------------------------------------------------
        # 9. Return final hybrid resolution.
        #
        # At this point the LLM definitely participated.
        # ---------------------------------------------------------

        return HybridResolution(
            settlement_id=settlement.settlement_id,
            action=policy_decision.action,
            candidate_ids=list(
                policy_decision.candidate_ids
            ),
            confidence=policy_decision.confidence,
            evidence_codes=list(
                policy_decision.evidence_codes
            ),
            reason=policy_decision.reason,
            llm_invoked=True,
        )

    @staticmethod
    def _to_domain_ledger(
        ledger,
    ) -> LedgerRecord:
        """
        Convert persistence-layer LedgerORM into a domain
        LedgerRecord.

        Domain reconciliation logic must not operate directly
        on ORM objects.
        """

        return LedgerRecord(
            ledger_id=ledger.ledger_id,
            merchant_id=ledger.merchant_id,
            amount=ledger.amount,
            currency=ledger.currency,
            transaction_date=ledger.transaction_date,
            reference=ledger.reference,
            entry_type=ledger.entry_type,
        )