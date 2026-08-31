from enum import Enum


class ReconciliationState(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


_ALLOWED_TRANSITIONS: dict[
    ReconciliationState,
    set[ReconciliationState],
] = {
    ReconciliationState.PENDING: {
        ReconciliationState.PROCESSING,
    },
    ReconciliationState.PROCESSING: {
        ReconciliationState.COMPLETED,
        ReconciliationState.FAILED,
    },
    ReconciliationState.COMPLETED: set(),
    ReconciliationState.FAILED: set(),
}


def can_transition(
    current: ReconciliationState,
    target: ReconciliationState,
) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def transition(
    current: ReconciliationState,
    target: ReconciliationState,
) -> ReconciliationState:
    if not can_transition(
        current,
        target,
    ):
        raise ValueError(
            f"Invalid reconciliation state transition: "
            f"{current.value} -> {target.value}"
        )

    return target