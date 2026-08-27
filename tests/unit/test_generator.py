from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.generator import DatasetGenerator
from app.domain.synthetic.models import ScenarioDistribution

import pytest

def test_generator_produces_dataset():
    distribution = ScenarioDistribution(
        counts={
            Scenario.EXACT_MATCH: 3,
        }
    )

    generator = DatasetGenerator(
        records=3,
        seed=42,
        distribution=distribution,
    )

    dataset = generator.generate()

    assert len(dataset.settlements) == 3
    assert len(dataset.ledger_records) == 3
    assert len(dataset.ground_truth) == 3

    assert dataset.scenario_by_settlement == {
        "S000001": Scenario.EXACT_MATCH,
        "S000002": Scenario.EXACT_MATCH,
        "S000003": Scenario.EXACT_MATCH,
    }


def test_generator_rejects_distribution_record_mismatch():
    distribution = ScenarioDistribution(
        counts={
            Scenario.EXACT_MATCH: 3,
        }
    )

    with pytest.raises(ValueError, match="records must equal"):
        DatasetGenerator(
            records=4,
            seed=42,
            distribution=distribution,
        )

def test_generator_is_reproducible():
    distribution = ScenarioDistribution(
        counts={
            Scenario.EXACT_MATCH: 3,
        }
    )

    first = DatasetGenerator(
        records=3,
        seed=42,
        distribution=distribution,
    ).generate()

    second = DatasetGenerator(
        records=3,
        seed=42,
        distribution=distribution,
    ).generate()

    assert first.model_dump() == second.model_dump()