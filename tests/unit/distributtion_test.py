from app.domain.synthetic.distribution import DEFAULT_DISTRIBUTION, Scenario


def test_default_distribution_totals_400():
    assert DEFAULT_DISTRIBUTION.total == 400

def test_default_distribution_contains_all_scenarios():
    assert set(DEFAULT_DISTRIBUTION.counts) == set(Scenario)