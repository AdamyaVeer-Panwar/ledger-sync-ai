from collections.abc import Callable

from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext, ScenarioResult
from app.domain.synthetic.scenarios import generate_exact_match

from app.domain.synthetic.scenarios import (
    generate_exact_match,
    generate_rounding_difference,
)


ScenarioGenerator = Callable[
    [ScenarioContext],
    ScenarioResult,
]


SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
}

SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
    Scenario.ROUNDING_DIFFERENCE: generate_rounding_difference,
}