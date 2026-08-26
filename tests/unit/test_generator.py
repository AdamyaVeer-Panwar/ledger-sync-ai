from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.generator import DatasetGenerator


def test_generator_produces_dataset():
    generator = DatasetGenerator(records=1, seed=42)

    dataset = generator.generate()

    assert len(dataset.settlements) == 1
    assert len(dataset.ledger_records) == 1

    assert dataset.ground_truth == {
        "S000001": "L000001",
    }

    assert dataset.scenario_by_settlement == {
        "S000001": Scenario.EXACT_MATCH,
    }