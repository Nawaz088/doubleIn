import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class BankConnection(BaseModel):
    __tablename__ = "bank_connections"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # qbo, xero, plaid
    external_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class BankTransaction(BaseModel):
    __tablename__ = "bank_transactions"

    bank_connection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bank_connections.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    classification_tier: Mapped[str] = mapped_column(String(20), default="unclassified")
    matched_transaction_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journal_entries.id"), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ClassificationRule(BaseModel):
    __tablename__ = "classification_rules"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    conditions: Mapped[dict] = mapped_column(JSON, nullable=False)
    actions: Mapped[dict] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)


class JournalEntry(BaseModel):
    __tablename__ = "journal_entries"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, recurring, accrual
    status: Mapped[str] = mapped_column(String(20), default="draft")
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[list["JournalEntryLine"]] = relationship(back_populates="journal_entry", cascade="all, delete-orphan")


class JournalEntryLine(BaseModel):
    __tablename__ = "journal_entry_lines"

    journal_entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    class_: Mapped[str | None] = mapped_column("class", String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="lines")
