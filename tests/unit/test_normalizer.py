from app.domain.reconciliation.normalizer import normalize_reference


def test_normalize_reference_strips_whitespace():
    assert normalize_reference("  UTR-123  ") == "utr123"


def test_normalize_reference_is_case_insensitive():
    assert normalize_reference("UtR-123") == "utr123"


def test_normalize_reference_removes_known_separator():
    assert normalize_reference("UTR-100007") == "utr100007"
    assert normalize_reference(" UTR100007 ") == "utr100007"


def test_normalize_reference_returns_none_for_missing_reference():
    assert normalize_reference(None) is None


def test_normalize_reference_returns_none_for_blank_reference():
    assert normalize_reference("   ") is None