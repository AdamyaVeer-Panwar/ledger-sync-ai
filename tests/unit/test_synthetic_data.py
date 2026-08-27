import random
from datetime import date

from app.domain.synthetic.models import ScenarioContext
from app.domain.synthetic.scenarios import generate_exact_match


def test_scenario_context():
    context = ScenarioContext(
        settlement_id="S000001",
        ledger_id="L000001",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    assert context.settlement_id == "S000001"
    assert context.ledger_id == "L000001"
    assert context.base_date == date(2026, 8, 25)


def test_exact_match_has_correct_ground_truth():
    context = ScenarioContext(
        settlement_id="S000001",
        ledger_id="L000001",
        rng=random.Random(42),
        base_date=date(2026, 8, 25),
    )

    result = generate_exact_match(context)

    assert result.scenario.value == "exact_match"
    assert len(result.settlements) == 1
    assert len(result.ledger_records) == 1

    assert result.ground_truth == {
        "S000001": "L000001",
    }