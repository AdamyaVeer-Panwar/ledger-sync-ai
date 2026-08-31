"""add run idempotency key

Revision ID: 91e2b13e2d23
Revises: c99ac4d619c0
Create Date: 2026-08-31 22:09:59.254952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91e2b13e2d23"
down_revision: Union[str, Sequence[str], None] = "c99ac4d619c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add and backfill reconciliation run idempotency keys."""

    # 1. Add the column as nullable so existing rows can survive.
    op.add_column(
        "reconciliation_runs",
        sa.Column(
            "idempotency_key",
            sa.String(length=128),
            nullable=True,
        ),
    )

    # 2. Backfill existing rows deterministically.
    op.execute(
        sa.text(
            """
            UPDATE reconciliation_runs
            SET idempotency_key = 'legacy-run-' || id::text
            WHERE idempotency_key IS NULL
            """
        )
    )

    # 3. Enforce the application invariant.
    op.alter_column(
        "reconciliation_runs",
        "idempotency_key",
        existing_type=sa.String(length=128),
        nullable=False,
    )

    # 4. Enforce uniqueness at the database layer.
    op.create_index(
        op.f("ix_reconciliation_runs_idempotency_key"),
        "reconciliation_runs",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    """Remove reconciliation run idempotency keys."""

    op.drop_index(
        op.f("ix_reconciliation_runs_idempotency_key"),
        table_name="reconciliation_runs",
    )

    op.drop_column(
        "reconciliation_runs",
        "idempotency_key",
    )