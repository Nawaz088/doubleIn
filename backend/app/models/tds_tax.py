import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


TDS_SECTIONS = {
    "194A": "Interest other than Interest on Securities",
    "194B": "Lotteries, Crossword Puzzle, etc.",
    "194C": "Contractor Payments",
    "194D": "Insurance Commission",
    "194E": "Non-Resident Sportsmen",
    "194EE": "Deposits under NSS",
    "194F": "Repurchase of Units by MF/UTI",
    "194G": "Commission on Sale of Lottery Tickets",
    "194H": "Commission/Brokerage",
    "194I": "Rent",
    "194IA": "TDS on Transfer of Immovable Property",
    "194IB": "TDS on Rent by Certain Individuals/HUF",
    "194IC": "TDS on Specified Agreement",
    "194J": "Professional/Technical Fees",
    "194JA": "TDS on Fees for Health Check-up",
    "194K": "Income from Units",
    "194L": "TDS on Compulsory Acquisition",
    "194LA": "TDS on Compensation for Acquired Property",
    "194LB": "Interest on Infrastructure Debt Fund",
    "194LC": "Interest on Foreign Loans",
    "194LD": "Interest on Certain Bonds",
    "194M": "TDS on Certain Payments by Individuals/HUF",
    "194N": "TDS on Cash Withdrawal",
    "194O": "TDS on E-Commerce Participants",
    "194P": "TDS for Senior Citizens",
    "194Q": "TDS on Purchase of Goods",
    "194R": "TDS on Benefits/Perquisites",
    "194S": "TDS on Virtual Digital Assets",
    "194T": "TDS on Payment of Rent by Certain Individuals",
}


class TdsRegistration(BaseModel):
    __tablename__ = "tds_registrations"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tan: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    pan_of_deductor: Mapped[str] = mapped_column(String(10), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deductor: Mapped[bool] = mapped_column(default=True)
    is_collector: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class TdsDeduction(BaseModel):
    __tablename__ = "tds_deductions"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tds_registration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tds_registrations.id"), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)
    deductor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deductor_pan: Mapped[str] = mapped_column(String(10), nullable=False)
    deductee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deductee_pan: Mapped[str] = mapped_column(String(10), nullable=False)
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tds_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    tds_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    surcharge: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    education_cess: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_tds: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    is_updated: Mapped[bool] = mapped_column(default=False)
    original_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    updated_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="deducted")
    challan_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    challan_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bsr_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    challan_serial: Mapped[str | None] = mapped_column(String(10), nullable=True)
    it_department_ack: Mapped[str | None] = mapped_column(String(50), nullable=True)


class TdsReturn(BaseModel):
    __tablename__ = "tds_returns"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tds_registration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tds_registrations.id"), nullable=False)
    form_type: Mapped[str] = mapped_column(String(10), nullable=False)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    token_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    acknowledgement: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_deductions: Mapped[int] = mapped_column(Integer, default=0)
    total_tds_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_deposited: Mapped[float] = mapped_column(Numeric(14, 2), default=0)


class TdsCertificate(BaseModel):
    __tablename__ = "tds_certificates"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    tds_deduction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tds_deductions.id"), nullable=False)
    certificate_type: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    certificate_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_of_issue: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_generated: Mapped[bool] = mapped_column(default=False)
    is_downloaded: Mapped[bool] = mapped_column(default=False)


class TcsCollection(BaseModel):
    __tablename__ = "tcs_collections"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(10), nullable=False)
    collector_name: Mapped[str] = mapped_column(String(255), nullable=False)
    collector_pan: Mapped[str] = mapped_column(String(10), nullable=False)
    collectee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    collectee_pan: Mapped[str] = mapped_column(String(10), nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    bill_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tcs_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    tcs_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    quarter: Mapped[str] = mapped_column(String(10), nullable=False)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="collected")
