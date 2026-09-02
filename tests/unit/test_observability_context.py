import structlog

from app.observability.logging import (
    bind_run_id,
    bind_settlement_id,
    clear_observability_context,
    clear_settlement_id,
    configure_logging,
    log_reconciliation_decision,
)


def _configure_test_logging():
    """
    Configure structlog with a capturing logger so the test can
    inspect the final event fields after contextvars are merged.
    """

    logger_factory = (
        structlog.testing.CapturingLoggerFactory()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
        ],
        logger_factory=logger_factory,
        cache_logger_on_first_use=False,
    )

    return logger_factory


def test_observability_context_correlates_run_and_settlement():
    factory = _configure_test_logging()

    clear_observability_context()

    try:
        bind_run_id(42)
        bind_settlement_id("S001")

        log_reconciliation_decision(
            decision="AUTO_MATCH",
            source="hybrid_resolver",
            confidence=1.0,
            selected_candidate_count=1,
            llm_invoked=False,
            duration_ms=12.5,
        )

        first_call = factory.logger.calls[-1]

        assert first_call.method_name == "info"
        assert first_call.kwargs["run_id"] == 42
        assert first_call.kwargs["settlement_id"] == "S001"
        assert first_call.kwargs["decision"] == "AUTO_MATCH"

        # Remove only the settlement-level context.
        clear_settlement_id()

        log_reconciliation_decision(
            decision="AUTO_MATCH",
            source="hybrid_resolver",
            confidence=1.0,
            selected_candidate_count=1,
            llm_invoked=False,
            duration_ms=8.2,
        )

        second_call = factory.logger.calls[-1]

        assert second_call.kwargs["run_id"] == 42
        assert "settlement_id" not in second_call.kwargs

    finally:
        clear_observability_context()


def test_settlement_context_does_not_leak_between_records():
    factory = _configure_test_logging()

    clear_observability_context()

    try:
        bind_run_id(99)

        # Record 1.
        bind_settlement_id("S001")

        log_reconciliation_decision(
            decision="AUTO_MATCH",
            source="hybrid_resolver",
            confidence=1.0,
            selected_candidate_count=1,
            llm_invoked=False,
            duration_ms=10.0,
        )

        first_call = factory.logger.calls[-1]

        assert first_call.kwargs["run_id"] == 99
        assert first_call.kwargs["settlement_id"] == "S001"

        clear_settlement_id()

        # Record 2.
        bind_settlement_id("S002")

        log_reconciliation_decision(
            decision="HUMAN_REVIEW",
            source="hybrid_resolver",
            confidence=0.0,
            selected_candidate_count=2,
            llm_invoked=False,
            duration_ms=11.0,
        )

        second_call = factory.logger.calls[-1]

        assert second_call.kwargs["run_id"] == 99
        assert second_call.kwargs["settlement_id"] == "S002"

        # Critical invariant:
        # S001 must not appear in the S002 event.
        assert second_call.kwargs["settlement_id"] != "S001"

    finally:
        clear_observability_context()