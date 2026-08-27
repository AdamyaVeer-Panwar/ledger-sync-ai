from app.domain.synthetic.enums import Scenario
from app.domain.synthetic.models import ScenarioDistribution


DEFAULT_DISTRIBUTION = ScenarioDistribution(
    counts={
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
)