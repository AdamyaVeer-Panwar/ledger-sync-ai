from app.domain.reconciliation.fusion_result import (
    EvidenceFusionResult,
    FusionAgreement,
)


def test_fusion_result_represents_strong_agreement():
    result = EvidenceFusionResult(
        candidate_ids=["L001"],
        agreement=FusionAgreement.STRONG_AGREEMENT,
        confidence=0.99,
        evidence_codes=[
            "amount_exact",
            "reference_exact",
        ],
    )

    assert result.candidate_ids == ["L001"]
    assert (
        result.agreement
        == FusionAgreement.STRONG_AGREEMENT
    )
    assert result.confidence == 0.99


def test_fusion_result_represents_llm_supported_result():
    result = EvidenceFusionResult(
        candidate_ids=["L001", "L002"],
        agreement=FusionAgreement.LLM_SUPPORTED,
        confidence=0.91,
        evidence_codes=[
            "multi_ledger_reasoning",
        ],
    )

    assert result.candidate_ids == [
        "L001",
        "L002",
    ]
    assert (
        result.agreement
        == FusionAgreement.LLM_SUPPORTED
    )


def test_fusion_result_represents_conflict():
    result = EvidenceFusionResult(
        candidate_ids=["L001"],
        agreement=FusionAgreement.CONFLICT,
        confidence=0.0,
        evidence_codes=[
            "rules_llm_disagreement",
        ],
    )

    assert (
        result.agreement
        == FusionAgreement.CONFLICT
    )


def test_fusion_result_represents_ambiguity():
    result = EvidenceFusionResult(
        candidate_ids=["L001", "L002"],
        agreement=FusionAgreement.AMBIGUOUS,
        confidence=0.5,
        evidence_codes=[
            "multiple_plausible_candidates",
        ],
    )

    assert (
        result.agreement
        == FusionAgreement.AMBIGUOUS
    )