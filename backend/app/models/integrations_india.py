import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class IndianBankConnection(BaseModel):
    __tablename__ = "indian_bank_connections"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(11), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_type: Mapped[str] = mapped_column(String(50), default="savings")
    upi_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_synced_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(20), default="not_connected")


class UpiTransaction(BaseModel):
    __tablename__ = "upi_transactions"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    bank_connection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("indian_bank_connections.id"), nullable=False)
    upi_transaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    upi_ref_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payer_vpa: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payee_vpa: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    transaction_date: Mapped[str] = mapped_column(String(30), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)


class ZohoBooksIntegration(BaseModel):
    __tablename__ = "zoho_books_integrations"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("clients.id"), nullable=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[str] = mapped_column(String(30), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(100), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    zoho_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_sync_at: Mapped[str | None] = mapped_column(String(30), nullable=True)


class TallyIntegration(BaseModel):
    __tablename__ = "tally_integrations"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("clients.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tally_company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    connection_type: Mapped[str] = mapped_column(String(20), default="xml")
    tally_host: Mapped[str] = mapped_column(String(255), default="localhost")
    tally_port: Mapped[int] = mapped_column(Integer, default=9000)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_sync_at: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sync_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
