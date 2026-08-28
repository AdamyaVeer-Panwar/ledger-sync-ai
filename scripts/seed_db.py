from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import csv

from app.db.models import (
    LedgerORM,
    ReconciliationRun,
    SettlementORM,
)
from app.db.session import SessionFactory


DATA_DIR = Path("data")


async def seed() -> None:
    async with SessionFactory() as session:
        run = ReconciliationRun(
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        session.add(run)
        await session.flush()

        with open(
            DATA_DIR / "settlements.csv",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                settlement = SettlementORM(
                    settlement_id=row["settlement_id"],
                    run_id=run.id,
                    merchant_id=row["merchant_id"],
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    settlement_date=datetime.strptime(
                        row["settlement_date"],
                        "%Y-%m-%d",
                    ).date(),
                    reference=row["reference"] or None,
                    created_at=datetime.now(timezone.utc),
                )

                session.add(settlement)

        with open(
            DATA_DIR / "ledger.csv",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                ledger = LedgerORM(
                    ledger_id=row["ledger_id"],
                    merchant_id=row["merchant_id"],
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    transaction_date=datetime.strptime(
                        row["transaction_date"],
                        "%Y-%m-%d",
                    ).date(),
                    reference=row["reference"] or None,
                    entry_type=row["entry_type"],
                    created_at=datetime.now(timezone.utc),
                )

                session.add(ledger)

        await session.commit()

        print("Database seeded successfully.")
        print(f"Run ID: {run.id}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed())