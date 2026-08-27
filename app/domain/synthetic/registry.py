from collections.abc import Callable

from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext, ScenarioResult
from app.domain.synthetic.scenarios import generate_exact_match

from app.domain.synthetic.scenarios import (
    generate_exact_match,
    generate_rounding_difference,
)
from app.domain.synthetic.scenarios import (
    generate_date_lag,
    generate_exact_match,
    generate_rounding_difference,
)

from app.domain.synthetic.scenarios import (
    generate_date_lag,
    generate_exact_match,
    generate_missing_reference,
    generate_rounding_difference,
)

from app.domain.synthetic.scenarios import (
    generate_date_lag,
    generate_exact_match,
    generate_missing_reference,
    generate_rounding_difference,
    generate_wrong_merchant,
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

SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
    Scenario.ROUNDING_DIFFERENCE: generate_rounding_difference,
    Scenario.DATE_LAG: generate_date_lag,
}

SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
    Scenario.ROUNDING_DIFFERENCE: generate_rounding_difference,
    Scenario.DATE_LAG: generate_date_lag,
    Scenario.MISSING_REFERENCE: generate_missing_reference,
}

SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
    Scenario.ROUNDING_DIFFERENCE: generate_rounding_difference,
    Scenario.DATE_LAG: generate_date_lag,
    Scenario.MISSING_REFERENCE: generate_missing_reference,
    Scenario.WRONG_MERCHANT: generate_wrong_merchant,
}