from collections.abc import Callable

from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioContext, ScenarioResult
from app.domain.synthetic.scenarios import generate_exact_match

from app.domain.synthetic.scenarios import (
    generate_corrupted_reference,
    generate_date_lag,
    generate_duplicate,
    generate_exact_match,
    generate_missing_ledger,
    generate_missing_reference,
    generate_rounding_difference,
    generate_wrong_merchant,
    generate_multiple_candidates,
)

ScenarioGenerator = Callable[
    [ScenarioContext],
    ScenarioResult,
]



SCENARIO_GENERATORS: dict[Scenario, ScenarioGenerator] = {
    Scenario.EXACT_MATCH: generate_exact_match,
    Scenario.ROUNDING_DIFFERENCE: generate_rounding_difference,
    Scenario.DATE_LAG: generate_date_lag,
    Scenario.MISSING_REFERENCE: generate_missing_reference,
    Scenario.WRONG_MERCHANT: generate_wrong_merchant,
    Scenario.MISSING_LEDGER: generate_missing_ledger,
    Scenario.CORRUPTED_REFERENCE: generate_corrupted_reference,
    Scenario.DUPLICATE: generate_duplicate,
    Scenario.MULTIPLE_CANDIDATES: generate_multiple_candidates,
}