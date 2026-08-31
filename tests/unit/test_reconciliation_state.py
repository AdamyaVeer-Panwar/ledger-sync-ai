import pytest

from app.domain.reconciliation.state import (
    ReconciliationState,
    can_transition,
    transition,
)


def test_pending_can_transition_to_processing():
    assert can_transition(
        ReconciliationState.PENDING,
        ReconciliationState.PROCESSING,
    )


def test_processing_can_transition_to_completed():
    assert can_transition(
        ReconciliationState.PROCESSING,
        ReconciliationState.COMPLETED,
    )


def test_processing_can_transition_to_failed():
    assert can_transition(
        ReconciliationState.PROCESSING,
        ReconciliationState.FAILED,
    )


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (
            ReconciliationState.COMPLETED,
            ReconciliationState.PROCESSING,
        ),
        (
            ReconciliationState.COMPLETED,
            ReconciliationState.FAILED,
        ),
        (
            ReconciliationState.PENDING,
            ReconciliationState.COMPLETED,
        ),
        (
            ReconciliationState.PENDING,
            ReconciliationState.FAILED,
        ),
        (
            ReconciliationState.FAILED,
            ReconciliationState.PROCESSING,
        ),
        (
            ReconciliationState.FAILED,
            ReconciliationState.COMPLETED,
        ),
    ],
)
def test_invalid_transitions_are_rejected(
    current,
    target,
):
    assert not can_transition(
        current,
        target,
    )

    with pytest.raises(ValueError):
        transition(
            current,
            target,
        )


def test_transition_returns_target_state():
    result = transition(
        ReconciliationState.PENDING,
        ReconciliationState.PROCESSING,
    )

    assert result == ReconciliationState.PROCESSING