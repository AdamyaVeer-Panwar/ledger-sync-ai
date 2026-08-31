import uuid

import asyncio

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionFactory
from app.repositories.run_repository import RunRepository


def unique_key(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"



@pytest.mark.asyncio
async def test_get_by_idempotency_key_returns_existing_run():
    idempotency_key = unique_key(
        "TEST-RUN-IDEMPOTENCY"
    )

    async with SessionFactory() as session:
        repository = RunRepository(session)

        run = await repository.create(
            idempotency_key=idempotency_key,
        )

        await session.commit()

    async with SessionFactory() as session:
        repository = RunRepository(session)

        found = await repository.get_by_idempotency_key(
            idempotency_key
        )

        assert found is not None
        assert found.id == run.id
        assert (
            found.idempotency_key
            == idempotency_key
        )


@pytest.mark.asyncio
async def test_get_by_idempotency_key_returns_none_for_unknown_key():
    idempotency_key = unique_key(
        "TEST-RUN-IDEMPOTENCY-NOT-FOUND"
    )

    async with SessionFactory() as session:
        repository = RunRepository(session)

        found = await repository.get_by_idempotency_key(
            idempotency_key
        )

        assert found is None


@pytest.mark.asyncio
async def test_create_assigns_unique_run_id():
    idempotency_key = unique_key(
        "TEST-RUN-IDEMPOTENCY-CREATE"
    )

    async with SessionFactory() as session:
        repository = RunRepository(session)

        run = await repository.create(
            idempotency_key=idempotency_key,
        )

        await session.commit()

        assert run.id is not None
        assert (
            run.idempotency_key
            == idempotency_key
        )
        assert run.status == "PENDING"
        assert run.created_at is not None


@pytest.mark.asyncio
async def test_duplicate_idempotency_key_is_rejected():
    idempotency_key = unique_key(
        "TEST-RUN-IDEMPOTENCY-DUPLICATE"
    )

    async with SessionFactory() as session:
        repository = RunRepository(session)

        await repository.create(
            idempotency_key=idempotency_key,
        )

        await session.commit()

    async with SessionFactory() as session:
        repository = RunRepository(session)

        with pytest.raises(IntegrityError):
            await repository.create(
                idempotency_key=idempotency_key,
            )

        await session.rollback()


@pytest.mark.asyncio
async def test_get_or_create_returns_same_run_for_same_key():
    idempotency_key = unique_key(
        "TEST-RUN-GET-OR-CREATE"
    )

    async with SessionFactory() as session:
        repository = RunRepository(session)

        first = await repository.get_or_create(
            idempotency_key=idempotency_key,
        )

        await session.commit()

    async with SessionFactory() as session:
        repository = RunRepository(session)

        second = await repository.get_or_create(
            idempotency_key=idempotency_key,
        )

        await session.commit()

    assert first.id == second.id
    assert (
        first.idempotency_key
        == second.idempotency_key
    )


@pytest.mark.asyncio
async def test_get_or_create_is_idempotent_under_concurrent_requests():
    idempotency_key = unique_key(
        "TEST-RUN-CONCURRENT"
    )

    async def create_or_get():
        async with SessionFactory() as session:
            repository = RunRepository(session)

            run = await repository.get_or_create(
                idempotency_key=idempotency_key,
            )

            await session.commit()

            return run.id

    run_ids = await asyncio.gather(
        create_or_get(),
        create_or_get(),
    )

    assert len(run_ids) == 2
    assert run_ids[0] == run_ids[1]

    async with SessionFactory() as session:
        repository = RunRepository(session)

        found = await repository.get_by_idempotency_key(
            idempotency_key
        )

        assert found is not None
        assert found.id == run_ids[0]