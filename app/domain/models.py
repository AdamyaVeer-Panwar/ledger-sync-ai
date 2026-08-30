from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import MatchStatus

from app.domain.enums import LedgerEntryType

class SettlementRecord(BaseModel):
    settlement_id: str
    merchant_id: str
    amount: Decimal = Field(gt=0)
    currency: str
    settlement_date: date
    reference: str | None = None


class LedgerRecord(BaseModel):
    ledger_id: str
    merchant_id: str
    amount: Decimal = Field(gt=0)
    currency: str
    transaction_date: date
    reference: str | None = None
    entry_type: LedgerEntryType


class MatchDecision(BaseModel):
    settlement_id: str
    status: MatchStatus

    candidate_ids: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence: list[str] = Field(
        default_factory=list
    )

    source: str


class ReconciliationRun(BaseModel):
    run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    total_records: int = Field(ge=0)
    matched_records: int = Field(ge=0)
    exception_records: int = Field(ge=0)