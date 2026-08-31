from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReconciliationRun


class RunRepository:
    """Persistence operations for reconciliation runs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> ReconciliationRun | None:
        result = await self.session.execute(
            select(ReconciliationRun).where(
                ReconciliationRun.idempotency_key
                == idempotency_key
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        idempotency_key: str,
        status: str = "PENDING",
    ) -> ReconciliationRun:
        run = ReconciliationRun(
            idempotency_key=idempotency_key,
            status=status,
            created_at=datetime.now(timezone.utc),
            completed_at=None,
        )

        self.session.add(run)
        await self.session.flush()

        return run

    async def get_or_create(
        self,
        *,
        idempotency_key: str,
        status: str = "PENDING",
    ) -> ReconciliationRun:
        existing = await self.get_by_idempotency_key(
            idempotency_key
        )

        if existing is not None:
            return existing

        try:
            return await self.create(
                idempotency_key=idempotency_key,
                status=status,
            )

        except IntegrityError:
            # Another concurrent request may have created the
            # same idempotency key after our initial lookup.
            await self.session.rollback()

            existing = await self.get_by_idempotency_key(
                idempotency_key
            )

            if existing is None:
                raise

            return existing