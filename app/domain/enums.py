from enum import Enum


class MatchStatus(str, Enum):
    PENDING = "PENDING"
    MATCHED_RULE = "MATCHED_RULE"
    MATCHED_AI = "MATCHED_AI"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    NO_MATCH = "NO_MATCH"
    FAILED = "FAILED"

class LedgerEntryType(str, Enum):
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"