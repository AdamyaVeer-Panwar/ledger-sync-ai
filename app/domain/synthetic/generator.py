from datetime import date
import random

from app.domain.synthetic.models import GeneratedDataset, ScenarioContext
from app.domain.synthetic.registry import SCENARIO_GENERATORS
from app.domain.synthetic.enums import Scenario


from datetime import date

from app.domain.synthetic.models import (
    GeneratedDataset,
    ScenarioContext,
)

class DatasetGenerator:
    def __init__(self, records: int, seed: int = 42) -> None:
        if records <= 0:
            raise ValueError("records must be greater than 0")

        self.records = records
        self.rng = random.Random(seed)

    def generate(self) -> GeneratedDataset:
        dataset = GeneratedDataset()

        scenario = Scenario.EXACT_MATCH
        scenario_generator = SCENARIO_GENERATORS[scenario]

        context = ScenarioContext(
            settlement_id="S000001",
            ledger_id="L000001",
            rng=self.rng,
            base_date=date(2026, 8, 25),
        )

        result = scenario_generator(context)

        dataset.settlements.extend(result.settlements)
        dataset.ledger_records.extend(result.ledger_records)
        dataset.ground_truth.update(result.ground_truth)

        for settlement_id in result.ground_truth:
            dataset.scenario_by_settlement[settlement_id] = result.scenario

        return dataset