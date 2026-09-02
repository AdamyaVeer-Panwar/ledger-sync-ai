from app.observability.metrics import (
    candidate_retrieval_candidates,
    candidate_retrieval_duration_seconds,
    candidate_retrieval_empty_total,
    candidate_retrieval_total,
)


def test_candidate_retrieval_metrics_exist():
    assert candidate_retrieval_total is not None
    assert candidate_retrieval_empty_total is not None
    assert candidate_retrieval_duration_seconds is not None
    assert candidate_retrieval_candidates is not None