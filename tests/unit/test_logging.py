import json

import structlog

from app.observability.logging import (
    bind_run_id,
    bind_settlement_id,
    clear_observability_context,
    configure_logging,
    log_reconciliation_decision,
)


def test_context_values_are_merged_into_structured_logs(
    capsys,
):
    clear_observability_context()

    configure_logging(
        json_logs=True,
    )

    bind_run_id(123)
    bind_settlement_id("S501")

    log_reconciliation_decision(
        decision="HUMAN_REVIEW",
        source="hybrid_resolver",
        confidence=0.72,
        selected_candidate_count=2,
        llm_invoked=False,
        duration_ms=382.1,
    )

    output = capsys.readouterr().out.strip()

    event = json.loads(output)

    assert event["event"] == "reconciliation_decision"
    assert event["run_id"] == 123
    assert event["settlement_id"] == "S501"
    assert event["decision"] == "HUMAN_REVIEW"
    assert event["confidence"] == 0.72
    assert event["selected_candidate_count"] == 2
    assert event["llm_invoked"] is False
    assert event["duration_ms"] == 382.1

    clear_observability_context()
    