import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.organization import User
from app.models.accounting import Client
from app.models.tds_tax import (
    TdsRegistration, TdsDeduction, TdsReturn, TdsCertificate, TcsCollection,
    TDS_SECTIONS,
)
from app.services.tds_engine import (
    get_tds_rate, calculate_tds, get_quarter_from_date, get_due_date,
    TDS_RATES,
)
from pydantic import BaseModel

router = APIRouter()


class TdsRegistrationCreate(BaseModel):
    client_id: uuid.UUID
    tan: str
    pan_of_deductor: str
    legal_name: str
    address: Optional[str] = None
    is_deductor: bool = True
    is_collector: bool = False


class TdsRegistrationResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    tan: str
    pan_of_deductor: str
    legal_name: str
    address: Optional[str] = None
    is_deductor: bool
    is_collector: bool
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class TdsDeductionCreate(BaseModel):
    client_id: uuid.UUID
    tds_registration_id: uuid.UUID
    section: str
    deductor_name: str
    deductor_pan: str
    deductee_name: str
    deductee_pan: str
    invoice_number: Optional[str] = None
    payment_date: date
    payment_amount: float
    tds_rate: float
    tds_amount: float
    surcharge: float = 0
    education_cess: float = 0
    total_tds: float
    quarter: str
    financial_year: str


class TdsDeductionResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    section: str
    deductor_name: str
    deductee_name: str
    deductee_pan: str
    payment_date: date
    payment_amount: float
    tds_rate: float
    tds_amount: float
    total_tds: float
    quarter: str
    financial_year: str
    status: str
    challan_cin: Optional[str] = None
    challan_date: Optional[date] = None

    model_config = {"from_attributes": True}


class TdsReturnCreate(BaseModel):
    client_id: uuid.UUID
    tds_registration_id: uuid.UUID
    form_type: str
    quarter: str
    financial_year: str
    due_date: date


class TdsReturnResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    form_type: str
    quarter: str
    financial_year: str
    due_date: date
    filing_date: Optional[date] = None
    status: str
    total_deductions: int
    total_tds_amount: float
    total_deposited: float
    acknowledgement: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/sections")
async def list_tds_sections():
    return [{"section": k, "name": v, "rate": TDS_RATES.get(k, {}).get("rate")} for k, v in TDS_SECTIONS.items()]


@router.post("/calculate")
async def compute_tds(
    section: str,
    payment_amount: float,
    is_company: bool = True,
    has_pan: bool = True,
):
    result = calculate_tds(section, payment_amount, is_company, has_pan)
    return result


@router.get("/registrations", response_model=list[TdsRegistrationResponse])
async def list_tds_registrations(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TdsRegistration).join(Client, TdsRegistration.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TdsRegistration.client_id == client_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/registrations", response_model=TdsRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_registration(
    req: TdsRegistrationCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    existing = await db.execute(select(TdsRegistration).where(TdsRegistration.tan == req.tan))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="TAN already registered")

    reg = TdsRegistration(**req.model_dump())
    db.add(reg)
    await db.commit()
    await db.refresh(reg)
    return reg


@router.get("/deductions", response_model=list[TdsDeductionResponse])
async def list_tds_deductions(
    client_id: uuid.UUID | None = Query(None),
    financial_year: str | None = Query(None),
    quarter: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TdsDeduction).join(Client, TdsDeduction.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TdsDeduction.client_id == client_id)
    if financial_year:
        query = query.where(TdsDeduction.financial_year == financial_year)
    if quarter:
        query = query.where(TdsDeduction.quarter == quarter)
    query = query.order_by(TdsDeduction.payment_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/deductions", response_model=TdsDeductionResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_deduction(
    req: TdsDeductionCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    deduction = TdsDeduction(**req.model_dump())
    db.add(deduction)
    await db.commit()
    await db.refresh(deduction)
    return deduction


@router.get("/returns", response_model=list[TdsReturnResponse])
async def list_tds_returns(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TdsReturn).join(Client, TdsReturn.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TdsReturn.client_id == client_id)
    query = query.order_by(TdsReturn.financial_year.desc(), TdsReturn.quarter.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/returns", response_model=TdsReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_return(
    req: TdsReturnCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    tds_return = TdsReturn(**req.model_dump())
    db.add(tds_return)
    await db.commit()
    await db.refresh(tds_return)
    return tds_return


@router.get("/summary")
async def get_tds_summary(
    client_id: uuid.UUID | None = Query(None),
    financial_year: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(
        TdsDeduction.section,
        func.count(TdsDeduction.id).label("count"),
        func.sum(TdsDeduction.payment_amount).label("total_payment"),
        func.sum(TdsDeduction.total_tds).label("total_tds"),
    ).join(Client, TdsDeduction.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TdsDeduction.client_id == client_id)
    if financial_year:
        query = query.where(TdsDeduction.financial_year == financial_year)
    query = query.group_by(TdsDeduction.section)
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "section": row.section,
            "count": row.count,
            "total_payment": float(row.total_payment),
            "total_tds": float(row.total_tds),
            "section_name": TDS_SECTIONS.get(row.section, ""),
        }
        for row in rows
    ]
