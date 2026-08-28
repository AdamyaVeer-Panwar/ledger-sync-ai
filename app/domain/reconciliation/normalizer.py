from dataclasses import dataclass

from app.domain.models import LedgerRecord, SettlementRecord


@dataclass(frozen=True)
class NormalizedSettlement:
    settlement: SettlementRecord
    normalized_reference: str | None


@dataclass(frozen=True)
class NormalizedLedger:
    ledger: LedgerRecord
    normalized_reference: str | None


def normalize_reference(reference: str | None) -> str | None:
    if reference is None:
        return None

    normalized = reference.strip().casefold()
    normalized = normalized.replace("-", "")

    return normalized or None


def normalize_settlement(
    settlement: SettlementRecord,
) -> NormalizedSettlement:
    return NormalizedSettlement(
        settlement=settlement,
        normalized_reference=normalize_reference(
            settlement.reference
        ),
    )


def normalize_ledger(
    ledger: LedgerRecord,
) -> NormalizedLedger:
    return NormalizedLedger(
        ledger=ledger,
        normalized_reference=normalize_reference(
            ledger.reference
        ),
    )