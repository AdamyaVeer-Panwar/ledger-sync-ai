import random
from datetime import date

from app.domain.synthetic.distribution import DEFAULT_DISTRIBUTION
from app.domain.synthetic.models import (
    GeneratedDataset,
    ScenarioContext,
    ScenarioDistribution,
)
from app.domain.synthetic.registry import SCENARIO_GENERATORS


class DatasetGenerator:
    def __init__(
        self,
        records: int,
        seed: int = 42,
        distribution: ScenarioDistribution | None = None,
    ) -> None:
        if records <= 0:
            raise ValueError("records must be greater than 0")

        self.records = records
        self.rng = random.Random(seed)
        self.distribution = distribution or DEFAULT_DISTRIBUTION

        if self.distribution.total != records:
            raise ValueError(
                "records must equal the total count in the scenario distribution"
            )

    def generate(self) -> GeneratedDataset:
        dataset = GeneratedDataset()

        settlement_number = 1
        ledger_number = 1

        for scenario, count in self.distribution.counts.items():
            scenario_generator = SCENARIO_GENERATORS.get(scenario)

            if scenario_generator is None:
                raise ValueError(
                    f"No generator registered for scenario: {scenario}"
                )

            for _ in range(count):
                settlement_id = f"S{settlement_number:06d}"
                ledger_id = f"L{ledger_number:06d}"

                context = ScenarioContext(
                    settlement_id=settlement_id,
                    ledger_id=ledger_id,
                    rng=self.rng,
                    base_date=date(2026, 8, 25),
                )

                result = scenario_generator(context)

                dataset.settlements.extend(result.settlements)
                dataset.ledger_records.extend(result.ledger_records)
                dataset.ground_truth.update(result.ground_truth)

                for result_settlement_id in result.ground_truth:
                    dataset.scenario_by_settlement[
                        result_settlement_id
                    ] = result.scenario

                settlement_number += len(result.settlements)
                ledger_number += len(result.ledger_records)

        return dataset