import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TaxReturn(BaseModel):
    __tablename__ = "tax_returns"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    form_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    filed_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class SignatureRequest(BaseModel):
    __tablename__ = "signature_requests"

    tax_return_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tax_returns.id"), nullable=False)
    signer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_url: Mapped[str] = mapped_column(String(500), nullable=False)
    auth_method: Mapped[str] = mapped_column(String(20), default="email")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TaxOrganizer(BaseModel):
    __tablename__ = "tax_organizers"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    form_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
