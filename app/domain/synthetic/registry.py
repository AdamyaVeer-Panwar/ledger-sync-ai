from collections.abc import Callable

from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext, ScenarioResult
from app.domain.synthetic.scenarios import generate_exact_match


ScenarioGenerator = Callable[
    [ScenarioContext],
    ScenarioResult,
]


SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
}