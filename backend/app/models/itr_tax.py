import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


ITR_FORM_TYPES = {
    "ITR1": "Sahaj (For individuals having income from salary, house property, etc.)",
    "ITR2": "For individuals/HUF not having business/profession income",
    "ITR3": "For individuals/HUF having income from business/profession",
    "ITR4": "Sugam (Presumptive income scheme for business/profession)",
    "ITR5": "For firms, LLPs, AOPs, BOIs, artificial juridical persons",
    "ITR6": "For companies other than companies claiming exemption under section 11",
    "ITR7": "For persons including companies required to furnish return under section 139(4A), 139(4B), 139(4C), 139(4D)",
}


class ItrFiling(BaseModel):
    __tablename__ = "itr_filings"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    assessment_year: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    form_type: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    gross_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_deductions: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    taxable_income: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_before_relief: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    rebate_87a: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_after_rebate: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    surcharge: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    education_cess: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_tax: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tds_credited: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    advance_tax_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    self_assessment_tax: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    interest_234a: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    interest_234b: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    interest_234c: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_tax_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    refund_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_payable: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    itr_acknowledgement: Mapped[str | None] = mapped_column(String(50), nullable=True)
    transaction_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    form_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_audited: Mapped[bool] = mapped_column(default=False)
    auditor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auditor_membership: Mapped[str | None] = mapped_column(String(20), nullable=True)
    old_regime: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Form26ASData(BaseModel):
    __tablename__ = "form_26as_data"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    pan: Mapped[str] = mapped_column(String(10), nullable=False)
    data_source: Mapped[str] = mapped_column(String(20), default="manual")
    tds_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tcs_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sxm_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    other_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_updated: Mapped[str | None] = mapped_column(String(30), nullable=True)


class AdvanceTaxInstallment(BaseModel):
    __tablename__ = "advance_tax_installments"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    installment_no: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    challan_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bsr_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")


class McaFiling(BaseModel):
    __tablename__ = "mca_filings"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    form_type: Mapped[str] = mapped_column(String(20), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    cin: Mapped[str | None] = mapped_column(String(21), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    registration_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    srn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    acknowledgement: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_adhp: Mapped[bool] = mapped_column(default=False)
    form_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class IncomeTaxNotice(BaseModel):
    __tablename__ = "income_tax_notices"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    notice_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    section: Mapped[str] = mapped_column(String(20), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    response_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="received")
    assessment_year: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    response_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
