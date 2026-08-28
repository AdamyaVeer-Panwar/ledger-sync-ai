import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionFactory


@pytest.mark.asyncio
async def test_database_connection():
    async with SessionFactory() as session:
        assert isinstance(session, AsyncSession)

        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1