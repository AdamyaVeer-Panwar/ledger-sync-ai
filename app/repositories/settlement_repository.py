from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SettlementORM


class SettlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        settlement: SettlementORM,
    ) -> SettlementORM:
        self.session.add(settlement)
        await self.session.flush()
        return settlement

    async def get_by_id(
        self,
        settlement_id: str,
    ) -> SettlementORM | None:
        result = await self.session.execute(
            select(SettlementORM).where(
                SettlementORM.settlement_id == settlement_id
            )
        )

        return result.scalar_one_or_none()