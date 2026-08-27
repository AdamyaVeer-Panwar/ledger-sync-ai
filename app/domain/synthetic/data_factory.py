import random
from datetime import date, timedelta
from decimal import Decimal


class SyntheticDataFactory:
    def __init__(self, rng: random.Random, base_date: date) -> None:
        self.rng = rng
        self.base_date = base_date

    def merchant_id(self) -> str:
        return f"M{self.rng.randint(1, 20):03d}"

    def amount(self) -> Decimal:
        cents = self.rng.randint(10_000, 1_000_000)
        return Decimal(cents) / Decimal("100")

    def transaction_date(self) -> date:
        offset = self.rng.randint(-5, 5)
        return self.base_date + timedelta(days=offset)

    @staticmethod
    def reference(settlement_id: str) -> str:
        return f"UTR-{settlement_id}"