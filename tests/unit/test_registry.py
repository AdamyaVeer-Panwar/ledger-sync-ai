from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.registry import SCENARIO_GENERATORS
from app.domain.synthetic.models import ScenarioContext
from app.domain.synthetic.registry import SCENARIO_GENERATORS



def test_exact_match_is_registered():
    assert Scenario.EXACT_MATCH in SCENARIO_GENERATORS



def test_registered_generator_is_callable():
    generator = SCENARIO_GENERATORS[Scenario.EXACT_MATCH]

    assert callable(generator)