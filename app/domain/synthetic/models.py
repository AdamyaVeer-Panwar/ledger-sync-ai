from pydantic import BaseModel, Field
from dataclasses import dataclass
from datetime import date
import random

from app.domain.models import LedgerRecord, SettlementRecord
from app.domain.synthetic.enums import Scenario

@dataclass
class ScenarioContext:
    settlement_id: str
    ledger_id: str
    rng: random.Random
    base_date: date
class ScenarioResult(BaseModel):
    scenario: Scenario
    settlements: list[SettlementRecord] = Field(default_factory=list)
    ledger_records: list[LedgerRecord] = Field(default_factory=list)
    ground_truth: dict[str, str | None] = Field(default_factory=dict)


class GeneratedDataset(BaseModel):
    settlements: list[SettlementRecord] = Field(default_factory=list)
    ledger_records: list[LedgerRecord] = Field(default_factory=list)
    ground_truth: dict[str, str | None] = Field(default_factory=dict)
    scenario_by_settlement: dict[str, Scenario] = Field(default_factory=dict)