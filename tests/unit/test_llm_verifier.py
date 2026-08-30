from app.domain.ai.models import (
    AIResolution,
    AIResolutionDecision,
)
from app.domain.enums import LedgerEntryType
from app.domain.models import (
    LedgerRecord,
    SettlementRecord,
)
from app.domain.reconciliation.llm_verifier import (
    LLMVerifier,
    VerificationStatus,
)


def make_settlement():
    return SettlementRecord(
        settlement_id="S001",
        merchant_id="M001",
        amount="1000.00",
        currency="INR",
        settlement_date="2026-08-25",
        reference="UTR-001",
    )


def make_ledger(
    *,
    ledger_id="L001",
    amount="1000.00",
    entry_type=LedgerEntryType.PAYMENT,
    merchant_id="M001",
):
    return LedgerRecord(
        ledger_id=ledger_id,
        merchant_id=merchant_id,
        amount=amount,
        currency="INR",
        transaction_date="2026-08-25",
        reference="UTR-001",
        entry_type=entry_type,
    )


def test_verifies_exact_single_candidate_match():
    verifier = LLMVerifier()

    resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=0.95,
        evidence_codes=[],
    )

    result = verifier.verify(
        settlement=make_settlement(),
        candidates=[
            make_ledger(),
        ],
        resolution=resolution,
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.candidate_ids == ["L001"]
    assert "amount_verified" in result.evidence_codes


def test_rejects_candidate_not_retrieved():
    verifier = LLMVerifier()

    resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L999"],
        confidence=1.0,
        evidence_codes=[],
    )

    result = verifier.verify(
        settlement=make_settlement(),
        candidates=[
            make_ledger(),
        ],
        resolution=resolution,
    )

    assert result.status == VerificationStatus.REJECTED
    assert result.candidate_ids == ["L999"]


def test_rejects_merchant_mismatch():
    verifier = LLMVerifier()

    resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=["L001"],
        confidence=1.0,
        evidence_codes=[],
    )

    result = verifier.verify(
        settlement=make_settlement(),
        candidates=[
            make_ledger(
                merchant_id="M002",
            ),
        ],
        resolution=resolution,
    )

    assert result.status == VerificationStatus.REJECTED
    assert "merchant_mismatch" in result.evidence_codes


def test_verifies_payment_refund_combination():
    verifier = LLMVerifier()

    settlement = SettlementRecord(
        settlement_id="S002",
        merchant_id="M009",
        amount="8081.06",
        currency="INR",
        settlement_date="2026-08-22",
        reference="UTR-S000259",
    )

    candidates = [
        LedgerRecord(
            ledger_id="L000297",
            merchant_id="M009",
            amount="8141.50",
            currency="INR",
            transaction_date="2026-08-22",
            reference="UTR-S000259",
            entry_type=LedgerEntryType.PAYMENT,
        ),
        LedgerRecord(
            ledger_id="L000298",
            merchant_id="M009",
            amount="60.44",
            currency="INR",
            transaction_date="2026-08-23",
            reference="UTR-S000259-REFUND",
            entry_type=LedgerEntryType.REFUND,
        ),
    ]

    resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=[
            "L000297",
            "L000298",
        ],
        confidence=1.0,
        evidence_codes=[
            "PARTIAL_REFUND",
        ],
    )

    result = verifier.verify(
        settlement=settlement,
        candidates=candidates,
        resolution=resolution,
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.candidate_ids == [
        "L000297",
        "L000298",
    ]
    assert (
        "multi_ledger_arithmetic_verified"
        in result.evidence_codes
    )


def test_returns_unverified_for_unproven_multi_candidate_relationship():
    verifier = LLMVerifier()

    resolution = AIResolution(
        decision=AIResolutionDecision.MATCH,
        candidate_ids=[
            "L001",
            "L002",
        ],
        confidence=0.95,
        evidence_codes=[],
    )

    result = verifier.verify(
        settlement=make_settlement(),
        candidates=[
            make_ledger(
                ledger_id="L001",
                amount="700.00",
            ),
            make_ledger(
                ledger_id="L002",
                amount="200.00",
            ),
        ],
        resolution=resolution,
    )

    assert result.status == VerificationStatus.UNVERIFIED
    assert result.candidate_ids == [
        "L001",
        "L002",
    ]


def test_verifies_valid_no_match():
    verifier = LLMVerifier()

    resolution = AIResolution(
        decision=AIResolutionDecision.NO_MATCH,
        candidate_ids=[],
        confidence=0.2,
        evidence_codes=[],
    )

    result = verifier.verify(
        settlement=make_settlement(),
        candidates=[
            make_ledger(),
        ],
        resolution=resolution,
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.candidate_ids == []
    assert "no_match" in result.evidence_codes