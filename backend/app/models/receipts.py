import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Receipt(BaseModel):
    __tablename__ = "receipts"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    upload_method: Mapped[str] = mapped_column(String(20), default="manual")
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing")
    matched_transaction_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journal_entries.id"), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccrualSchedule(BaseModel):
    __tablename__ = "accrual_schedules"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recognition_method: Mapped[str] = mapped_column(String(20), default="straight_line")
    journal_entry_template: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    entries: Mapped[list["AccrualEntry"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")


class AccrualEntry(BaseModel):
    __tablename__ = "accrual_entries"

    schedule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accrual_schedules.id"), nullable=False, index=True)
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    recognized_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("journal_entries.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    schedule: Mapped["AccrualSchedule"] = relationship(back_populates="entries")
