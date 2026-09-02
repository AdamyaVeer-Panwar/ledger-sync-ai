import logging
import sys

import structlog


def configure_logging(
    *,
    json_logs: bool = False,
    log_level: int = logging.INFO,
) -> None:
    """
    Configure application-wide structured logging.

    Development:
        json_logs=False
        -> human-readable console output

    Production:
        json_logs=True
        -> machine-readable JSON output

    Context-local fields such as request_id, run_id, and
    settlement_id are merged into every structlog event.
    """

    renderer: structlog.types.Processor

    if json_logs:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.StackInfoRenderer(),
    ]

    # JSON output needs explicit exception serialization.
    #
    # ConsoleRenderer already handles exc_info itself, so we do
    # not add format_exc_info in development mode.
    if json_logs:
        processors.append(
            structlog.processors.format_exc_info
        )

    processors.append(renderer)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            log_level
        ),
        logger_factory=structlog.PrintLoggerFactory(
            file=sys.stdout
        ),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.BoundLogger:
    """
    Return the application logger.
    """

    return structlog.get_logger()


# ---------------------------------------------------------------------------
# Correlation context
# ---------------------------------------------------------------------------

def bind_request_id(
    request_id: str,
) -> None:
    """
    Bind an HTTP/request correlation identifier.

    The value is automatically included in subsequent structured
    log events within the current context.
    """

    structlog.contextvars.bind_contextvars(
        request_id=request_id,
    )


def bind_run_id(
    run_id: int,
) -> None:
    """
    Bind the reconciliation run identifier.
    """

    structlog.contextvars.bind_contextvars(
        run_id=run_id,
    )


def bind_settlement_id(
    settlement_id: str,
) -> None:
    """
    Bind the settlement identifier for the current record.
    """

    structlog.contextvars.bind_contextvars(
        settlement_id=settlement_id,
    )


def clear_settlement_id() -> None:
    """
    Remove only the settlement-specific correlation field.

    Run-level context remains intact.
    """

    structlog.contextvars.unbind_contextvars(
        "settlement_id",
    )


def clear_observability_context() -> None:
    """
    Clear all observability context at the end of a logical
    execution boundary such as a reconciliation run or request.
    """

    structlog.contextvars.clear_contextvars()


# ---------------------------------------------------------------------------
# Reconciliation events
# ---------------------------------------------------------------------------

def log_reconciliation_decision(
    *,
    decision: str,
    source: str,
    confidence: float,
    selected_candidate_count: int,
    llm_invoked: bool,
    duration_ms: float,
) -> None:
    """
    Emit the final reconciliation decision.

    Correlation identifiers are obtained automatically from
    structlog contextvars.
    """

    logger = get_logger()

    logger.info(
        "reconciliation_decision",
        decision=decision,
        source=source,
        confidence=confidence,
        selected_candidate_count=selected_candidate_count,
        llm_invoked=llm_invoked,
        duration_ms=round(
            duration_ms,
            2,
        ),
    )


def log_reconciliation_failure(
    *,
    error_type: str,
    duration_ms: float,
) -> None:
    """
    Emit a record-processing failure event.

    Correlation identifiers are obtained automatically from
    structlog contextvars.
    """

    logger = get_logger()

    logger.error(
        "reconciliation_failure",
        error_type=error_type,
        duration_ms=round(
            duration_ms,
            2,
        ),
    )


def log_rule_evaluation(
    *,
    decision: str,
    confidence: float,
    candidate_count: int,
) -> None:
    """
    Emit the deterministic rule-engine outcome.
    """

    logger = get_logger()

    logger.info(
        "rule_evaluation",
        decision=decision,
        confidence=confidence,
        candidate_count=candidate_count,
    )


def log_candidate_retrieval(
    *,
    candidate_count: int,
    duration_ms: float,
) -> None:
    """
    Emit the result of bounded candidate retrieval.

    Correlation identifiers are obtained automatically from
    structlog contextvars.
    """

    logger = get_logger()

    logger.info(
        "candidate_retrieval",
        candidate_count=candidate_count,
        duration_ms=round(
            duration_ms,
            2,
        ),
    )


def log_llm_verification(
    *,
    status: str,
    candidate_count: int,
    reason: str,
) -> None:
    """
    Emit the deterministic verification result for an LLM proposal.
    """

    logger = get_logger()

    logger.info(
        "llm_verification",
        status=status,
        candidate_count=candidate_count,
        reason=reason,
    )


def log_evidence_fusion(
    *,
    agreement: str,
    candidate_count: int,
    confidence: float,
) -> None:
    """
    Emit the result of combining deterministic and AI evidence.
    """

    logger = get_logger()

    logger.info(
        "evidence_fusion",
        agreement=agreement,
        candidate_count=candidate_count,
        confidence=confidence,
    )


def log_policy_decision(
    *,
    action: str,
    candidate_count: int,
    confidence: float,
    reason: str,
) -> None:
    """
    Emit the final policy authorization decision.
    """

    logger = get_logger()

    logger.info(
        "policy_decision",
        action=action,
        candidate_count=candidate_count,
        confidence=confidence,
        reason=reason,
    )


def log_llm_invocation(
    *,
    model: str,
    candidate_count: int,
    status: str,
    duration_ms: float,
    error_type: str | None = None,
) -> None:
    """
    Emit metadata about one LLM resolution attempt.

    Prompt and model response are intentionally not logged.
    """

    logger = get_logger()

    logger.info(
        "llm_invocation",
        model=model,
        candidate_count=candidate_count,
        status=status,
        duration_ms=round(
            duration_ms,
            2,
        ),
        error_type=error_type,
    )