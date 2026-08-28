from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LedgerORM


class LedgerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, ledger: LedgerORM) -> LedgerORM:
        self.session.add(ledger)
        await self.session.flush()
        return ledger

    async def get_by_id(
        self,
        ledger_id: str,
    ) -> LedgerORM | None:
        result = await self.session.execute(
            select(LedgerORM).where(
                LedgerORM.ledger_id == ledger_id
            )
        )
        return result.scalar_one_or_none()

    async def find_candidates(
        self,
        *,
        merchant_id: str,
        amount: Decimal,
        transaction_date: date,
        date_window_days: int = 0,
    ) -> list[LedgerORM]:
        start_date = transaction_date - timedelta(
            days=date_window_days
        )
        end_date = transaction_date + timedelta(
            days=date_window_days
        )

        stmt = (
            select(LedgerORM)
            .where(
                LedgerORM.merchant_id == merchant_id,
                LedgerORM.amount == amount,
                LedgerORM.transaction_date.between(
                    start_date,
                    end_date,
                ),
            )
            .order_by(
                LedgerORM.transaction_date,
                LedgerORM.ledger_id,
            )
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_reference_and_amount(
        self,
        *,
        reference: str,
        amount: Decimal,
    ) -> list[LedgerORM]:
        stmt = (
            select(LedgerORM)
            .where(
                LedgerORM.reference == reference,
                LedgerORM.amount == amount,
            )
            .order_by(LedgerORM.ledger_id)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())