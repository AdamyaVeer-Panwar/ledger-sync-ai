from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    settlements: Mapped[list["SettlementORM"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )
    match_results: Mapped[list["MatchResultORM"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )
    audit_events: Mapped[list["AuditEventORM"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class SettlementORM(Base):
    __tablename__ = "settlement_records"

    settlement_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reconciliation_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    merchant_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    settlement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    reference: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    run: Mapped["ReconciliationRun"] = relationship(
        back_populates="settlements",
    )

    match_results: Mapped[list["MatchResultORM"]] = relationship(
        back_populates="settlement",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="amount_positive",
        ),
        Index(
            "ix_settlement_merchant_date",
            "merchant_id",
            "settlement_date",
        ),
        Index(
            "ix_settlement_merchant_amount",
            "merchant_id",
            "amount",
        ),
    )


class LedgerORM(Base):
    __tablename__ = "ledger_records"

    ledger_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    merchant_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    transaction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    reference: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    entry_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    match_links: Mapped[list["MatchResultLedgerORM"]] = relationship(
        back_populates="ledger",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="amount_positive",
        ),
        Index(
            "ix_ledger_merchant_date",
            "merchant_id",
            "transaction_date",
        ),
        Index(
            "ix_ledger_merchant_amount",
            "merchant_id",
            "amount",
        ),
    )


class MatchResultORM(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reconciliation_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    settlement_id: Mapped[str] = mapped_column(
        ForeignKey(
            "settlement_records.settlement_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    evidence: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    run: Mapped["ReconciliationRun"] = relationship(
        back_populates="match_results",
    )

    settlement: Mapped["SettlementORM"] = relationship(
        back_populates="match_results",
    )

    ledger_links: Mapped[list["MatchResultLedgerORM"]] = relationship(
        back_populates="match_result",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="confidence_range",
        ),
        UniqueConstraint(
            "run_id",
            "settlement_id",
            name="uq_match_result_run_settlement",
        ),
    )


class MatchResultLedgerORM(Base):
    __tablename__ = "match_result_ledgers"

    match_result_id: Mapped[int] = mapped_column(
        ForeignKey(
            "match_results.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    ledger_id: Mapped[str] = mapped_column(
        ForeignKey(
            "ledger_records.ledger_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    match_result: Mapped["MatchResultORM"] = relationship(
        back_populates="ledger_links",
    )

    ledger: Mapped["LedgerORM"] = relationship(
        back_populates="match_links",
    )


class AuditEventORM(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "reconciliation_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    entity_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    details: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    run: Mapped["ReconciliationRun"] = relationship(
        back_populates="audit_events",
    )