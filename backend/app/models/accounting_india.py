import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


INDIAN_ENTITY_TYPES = [
    "private_limited", "public_limited", "limited_liability_partnership",
    "partnership_firm", "sole_proprietorship", "one_person_company",
    "section_8_company", "producer_company", "hindu_undivided_family",
    "association_of_persons", "body_of_individuals", "trust",
    "cooperative_society", "government_body", "foreign_company",
]

ENTITY_TYPE_MAP = {
    "llc": "private_limited",
    "corp": "public_limited",
    "sole_prop": "sole_proprietorship",
}


class IndianChartOfAccount(BaseModel):
    __tablename__ = "indian_chart_of_accounts"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_schedule_iii: Mapped[bool] = mapped_column(default=False)
    parent_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class IndianFinancialYear(BaseModel):
    __tablename__ = "indian_financial_years"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    fy: Mapped[str] = mapped_column(String(9), nullable=False)
    start_date: Mapped[str] = mapped_column(String(10), nullable=False)
    end_date: Mapped[str] = mapped_column(String(10), nullable=False)
    is_current: Mapped[bool] = mapped_column(default=False)
    is_locked: Mapped[bool] = mapped_column(default=False)
    previous_fy: Mapped[str | None] = mapped_column(String(9), nullable=True)
