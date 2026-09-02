from app.observability.metrics import (
    llm_calls_total,
    llm_failures_total,
    llm_latency_seconds,
    reconciliation_duration_seconds,
    reconciliation_exceptions_total,
    reconciliation_matches_total,
    reconciliation_records_total,
)
from prometheus_client import REGISTRY

from app.observability.metrics import (
    reconciliation_duration_seconds,
    reconciliation_exceptions_total,
    reconciliation_matches_total,
    reconciliation_records_total,
)

def test_metrics_are_registered():
    assert reconciliation_records_total is not None
    assert reconciliation_matches_total is not None
    assert reconciliation_exceptions_total is not None
    assert llm_calls_total is not None
    assert llm_failures_total is not None
    assert reconciliation_duration_seconds is not None
    assert llm_latency_seconds is not None

def test_reconciliation_metrics_are_registered():
    assert reconciliation_records_total is not None
    assert reconciliation_matches_total is not None
    assert reconciliation_exceptions_total is not None
    assert reconciliation_duration_seconds is not None

    assert (
        REGISTRY._names_to_collectors.get(
            "reconciliation_records_total"
        )
        is not None
    )