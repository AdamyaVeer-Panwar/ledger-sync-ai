from enum import Enum


class Scenario(str, Enum):
    EXACT_MATCH = "exact_match"
    ROUNDING_DIFFERENCE = "rounding_difference"
    DATE_LAG = "date_lag"
    MISSING_REFERENCE = "missing_reference"
    DUPLICATE = "duplicate"
    PARTIAL_REFUND = "partial_refund"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    WRONG_MERCHANT = "wrong_merchant"
    MISSING_LEDGER = "missing_ledger"
    CORRUPTED_REFERENCE = "corrupted_reference"