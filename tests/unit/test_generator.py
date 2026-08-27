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



def test_generator_produces_valid_400_record_dataset():
    generator = DatasetGenerator(
        records=400,
        seed=42,
    )

    dataset = generator.generate()

    assert len(dataset.settlements) == 400
    assert len(dataset.ground_truth) == 400

    settlement_ids = [
        settlement.settlement_id
        for settlement in dataset.settlements
    ]

    ledger_ids = [
        ledger.ledger_id
        for ledger in dataset.ledger_records
    ]

    # Every settlement ID must be unique.
    assert len(settlement_ids) == len(settlement_ids)

    # Every ledger ID must be globally unique.
    assert len(set(ledger_ids)) == len(ledger_ids)

    all_ledger_ids = set(ledger_ids)

    # Every ground-truth ledger reference must exist.
    for truth_ledger_ids in dataset.ground_truth.values():
        if truth_ledger_ids is not None:
            for ledger_id in truth_ledger_ids:
                assert ledger_id in all_ledger_ids

    # Every generated settlement must have exactly one ground-truth entry.
    assert set(settlement_ids) == set(dataset.ground_truth.keys())

    # Every settlement must have scenario metadata.
    assert set(settlement_ids) == set(
        dataset.scenario_by_settlement.keys()
    )

def test_generator_produces_expected_scenario_distribution():
    generator = DatasetGenerator(
        records=400,
        seed=42,
    )

    dataset = generator.generate()

    scenario_counts = {}

    for scenario in dataset.scenario_by_settlement.values():
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

    assert scenario_counts == {
        Scenario.EXACT_MATCH: 100,
        Scenario.ROUNDING_DIFFERENCE: 40,
        Scenario.DATE_LAG: 40,
        Scenario.MISSING_REFERENCE: 40,
        Scenario.DUPLICATE: 35,
        Scenario.PARTIAL_REFUND: 30,
        Scenario.MULTIPLE_CANDIDATES: 35,
        Scenario.WRONG_MERCHANT: 30,
        Scenario.MISSING_LEDGER: 30,
        Scenario.CORRUPTED_REFERENCE: 20,
    }