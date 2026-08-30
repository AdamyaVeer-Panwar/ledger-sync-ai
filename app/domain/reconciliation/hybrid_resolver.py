from decimal import Decimal

from app.domain.models import LedgerRecord, SettlementRecord
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
        confident?
          ├── YES → AUTO_MATCH
          │
          └── NO
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
        #
        # Candidate retrieval is infrastructure work. The returned
        # ORM records are converted into domain LedgerRecord objects
        # before entering the domain reconciliation logic.
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
        # 3. Strong deterministic result.
        #
        # Do not invoke the LLM when deterministic evidence is
        # already sufficient.
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
            )

        # ---------------------------------------------------------
        # 4. Rules are insufficient.
        #
        # Ask the LLM to reason over the bounded candidate set.
        # ---------------------------------------------------------

        ai_result = await self.llm_resolver.resolve(
            settlement,
            candidates,
        )

        # ---------------------------------------------------------
        # 5. Deterministically verify the LLM proposal.
        #
        # The LLM is allowed to propose.
        # The verifier determines whether that proposal is supported
        # by objective evidence.
        # ---------------------------------------------------------

        verification_result = self.verifier.verify(
            settlement=settlement,
            candidates=candidates,
            resolution=ai_result.resolution,
        )

        # ---------------------------------------------------------
        # 6. Fuse rule evidence + AI evidence + verification.
        # ---------------------------------------------------------

        fusion_result = self.fusion.fuse(
            rule_result,
            ai_result.resolution,
            verification_result,
        )

        # ---------------------------------------------------------
        # 7. Policy is the final authorization boundary.
        # ---------------------------------------------------------

        policy_decision = self.policy.evaluate(
            fusion_result
        )

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
        )

    @staticmethod
    def _to_domain_ledger(
        ledger,
    ) -> LedgerRecord:
        """
        Convert persistence-layer LedgerORM into a domain LedgerRecord.

        Domain reconciliation logic must not operate directly on ORM
        objects.
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