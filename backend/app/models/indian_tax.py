import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class GstRegistration(BaseModel):
    __tablename__ = "gst_registrations"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    gstin: Mapped[str] = mapped_column(String(15), nullable=False, unique=True, index=True)
    trade_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state_name: Mapped[str] = mapped_column(String(100), nullable=False)
    registration_type: Mapped[str] = mapped_column(String(20), default="regular")
    taxpayer_type: Mapped[str] = mapped_column(String(20), default="regular")
    constitution: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    registration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cancellation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    filing_frequency: Mapped[str] = mapped_column(String(20), default="monthly")
    is_composition: Mapped[bool] = mapped_column(default=False)
    e_invoice_enabled: Mapped[bool] = mapped_column(default=False)
    e_waybill_enabled: Mapped[bool] = mapped_column(default=False)
    gst_practice_head: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class HsnSacCode(BaseModel):
    __tablename__ = "hsn_sac_codes"

    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(10), default="hsn")
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    cgst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    sgst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    igst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    cess_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    compensation_cess: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    chapter: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class GstInvoice(BaseModel):
    __tablename__ = "gst_invoices"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    gst_registration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gst_registrations.id"), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(20), default="regular")
    supply_type: Mapped[str] = mapped_column(String(20), default="goods")
    supply_place: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inter_state: Mapped[bool] = mapped_column(default=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    customer_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    total_taxable_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    total_cgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_sgst: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_igst: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_cess: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_invoice_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    e_invoice_irn: Mapped[str | None] = mapped_column(String(100), nullable=True)
    e_waybill_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    irn_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    irn_status: Mapped[str] = mapped_column(String(20), default="not_generated")
    filed_in_gstr: Mapped[bool] = mapped_column(default=False)
    gstr_period: Mapped[str | None] = mapped_column(String(7), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class GstInvoiceLine(BaseModel):
    __tablename__ = "gst_invoice_lines"

    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gst_invoices.id"), nullable=False, index=True)
    hsn_sac_code: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    taxable_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    cgst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    sgst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    igst_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    cgst_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    sgst_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    igst_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    cess_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class GstReturn(BaseModel):
    __tablename__ = "gst_returns"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    gst_registration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("gst_registrations.id"), nullable=False)
    return_type: Mapped[str] = mapped_column(String(20), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    return_period: Mapped[str] = mapped_column(String(7), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total_outward_taxable: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_outward_tax: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_inward_taxable: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_inward_tax: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_liability: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_credit: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    net_payable: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    itc_claimed: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    late_fee: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    interest: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    arn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    filed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
