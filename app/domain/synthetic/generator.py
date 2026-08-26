import random

from app.domain.synthetic.models import GeneratedDataset
from app.domain.synthetic.scenarios import generate_exact_match


class DatasetGenerator:
    def __init__(self, records: int, seed: int = 42) -> None:
        if records <= 0:
            raise ValueError("records must be greater than 0")

        self.records = records
        self.rng = random.Random(seed)

    def generate(self) -> GeneratedDataset:
        dataset = GeneratedDataset()

        result = generate_exact_match(
            settlement_id="S000001",
            ledger_id="L000001",
        )

        dataset.settlements.extend(result.settlements)
        dataset.ledger_records.extend(result.ledger_records)
        dataset.ground_truth.update(result.ground_truth)

        for settlement_id in result.ground_truth:
            dataset.scenario_by_settlement[settlement_id] = result.scenario

        return dataset