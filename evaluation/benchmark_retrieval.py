import asyncio
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LedgerORM
from app.db.session import SessionFactory
from app.domain.enums import LedgerEntryType
from app.repositories.candidate_retriever import CandidateRetriever


BENCHMARK_MERCHANT = "BENCHMARK-MERCHANT"
BENCHMARK_CURRENCY = "INR"
BENCHMARK_DATE = date(2026, 8, 25)
BENCHMARK_AMOUNT = Decimal("1000.00")


def build_ledger_rows(count: int) -> list[LedgerORM]:
    rows: list[LedgerORM] = []

    for i in range(count):
        if i < 20:
            merchant_id = BENCHMARK_MERCHANT
            amount = BENCHMARK_AMOUNT
            currency = BENCHMARK_CURRENCY
            transaction_date = BENCHMARK_DATE + timedelta(
                days=i % 3
            )
        else:
            merchant_id = f"M-{i:05d}"
            amount = Decimal("1000.00") + (
                Decimal(i % 100) / 100
            )
            currency = "USD"
            transaction_date = (
                BENCHMARK_DATE
                + timedelta(days=i % 30)
            )

        rows.append(
            LedgerORM(
                ledger_id=f"BENCH-L-{i:08d}",
                merchant_id=merchant_id,
                amount=amount,
                currency=currency,
                transaction_date=transaction_date,
                reference=f"BENCH-REF-{i:08d}",
                entry_type=LedgerEntryType.PAYMENT.value,
                created_at=datetime.now(timezone.utc),
            )
        )

    return rows


async def clear_benchmark_rows(
    session: AsyncSession,
) -> None:
    await session.execute(
        delete(LedgerORM).where(
            LedgerORM.ledger_id.like("BENCH-L-%")
        )
    )
    await session.commit()


async def run_benchmark(count: int) -> None:
    async with SessionFactory() as session:

        # Always start from a clean benchmark state.
        await clear_benchmark_rows(session)

        rows = build_ledger_rows(count)

        start_insert = time.perf_counter()

        session.add_all(rows)
        await session.commit()

        insert_time = (
            time.perf_counter() - start_insert
        )

        retriever = CandidateRetriever(session)

        # Warm-up query.
        await retriever.retrieve(
            merchant_id=BENCHMARK_MERCHANT,
            currency=BENCHMARK_CURRENCY,
            amount=BENCHMARK_AMOUNT,
            transaction_date=BENCHMARK_DATE,
            amount_tolerance=Decimal("0.02"),
            date_window_days=2,
            limit=50,
        )

        start_query = time.perf_counter()

        candidates = await retriever.retrieve(
            merchant_id=BENCHMARK_MERCHANT,
            currency=BENCHMARK_CURRENCY,
            amount=BENCHMARK_AMOUNT,
            transaction_date=BENCHMARK_DATE,
            amount_tolerance=Decimal("0.02"),
            date_window_days=2,
            limit=50,
        )

        query_time = (
            time.perf_counter() - start_query
        )

        print()
        print(f"Dataset size       : {count:,}")
        print(
            f"Insert time        : "
            f"{insert_time:.4f} sec"
        )
        print(
            f"Query time         : "
            f"{query_time * 1000:.3f} ms"
        )
        print(
            f"Candidates returned: "
            f"{len(candidates)}"
        )

        # IMPORTANT:
        # Keep benchmark rows in PostgreSQL so we can
        # inspect the 100k query with EXPLAIN ANALYZE.
        #
        # Cleanup happens at the beginning of the next
        # benchmark run.


async def main() -> None:
    print("Candidate Retrieval Benchmark")
    print("=============================")

    await run_benchmark(10_000)
    await run_benchmark(100_000)


if __name__ == "__main__":
    asyncio.run(main())