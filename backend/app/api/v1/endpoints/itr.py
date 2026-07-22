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
from app.models.itr_tax import (
    ItrFiling, Form26ASData, AdvanceTaxInstallment, McaFiling, IncomeTaxNotice,
    ITR_FORM_TYPES,
)
from app.services.itr_engine import (
    calculate_income_tax, get_itr_due_date, get_assessment_year,
    get_advance_tax_schedule,
)
from pydantic import BaseModel

router = APIRouter()


class TaxCalcRequest(BaseModel):
    gross_income: float
    deductions_80c: float = 0
    deductions_80d: float = 0
    deductions_80g: float = 0
    deductions_80e: float = 0
    hra_exemption: float = 0
    lta_exemption: float = 0
    other_exemptions: float = 0
    old_regime: bool = True
    is_senior: bool = False
    tds_credited: float = 0
    advance_tax_paid: float = 0


class ItrFilingCreate(BaseModel):
    client_id: uuid.UUID
    financial_year: str
    form_type: str
    due_date: Optional[date] = None
    assigned_to: Optional[uuid.UUID] = None
    gross_income: float = 0


class ItrFilingUpdate(BaseModel):
    status: Optional[str] = None
    filing_date: Optional[date] = None
    gross_income: Optional[float] = None
    total_deductions: Optional[float] = None
    taxable_income: Optional[float] = None
    total_tax: Optional[float] = None
    tds_credited: Optional[float] = None
    total_tax_paid: Optional[float] = None
    refund_amount: Optional[float] = None
    tax_payable: Optional[float] = None
    itr_acknowledgement: Optional[str] = None
    form_data: Optional[dict] = None
    notes: Optional[str] = None


class ItrFilingResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    assessment_year: str
    financial_year: str
    form_type: str
    status: str
    due_date: Optional[date] = None
    filing_date: Optional[date] = None
    gross_income: float
    taxable_income: float
    total_tax: float
    tds_credited: float
    refund_amount: float
    tax_payable: float
    itr_acknowledgement: Optional[str] = None
    old_regime: bool

    model_config = {"from_attributes": True}


class AdvanceTaxResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    financial_year: str
    installment_no: int
    due_date: date
    amount_due: float
    amount_paid: float
    status: str

    model_config = {"from_attributes": True}


class McaFilingCreate(BaseModel):
    client_id: uuid.UUID
    financial_year: str
    form_type: str
    due_date: date
    cin: Optional[str] = None
    company_name: str
    registration_number: Optional[str] = None


class McaFilingResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    financial_year: str
    form_type: str
    due_date: date
    filing_date: Optional[date] = None
    status: str
    cin: Optional[str] = None
    company_name: str
    srn: Optional[str] = None
    acknowledgement: Optional[str] = None

    model_config = {"from_attributes": True}


class IncomeTaxNoticeResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    notice_type: str
    notice_number: str
    section: str
    issue_date: date
    response_deadline: Optional[date] = None
    status: str
    assessment_year: str

    model_config = {"from_attributes": True}


@router.get("/form-types")
async def list_itr_forms():
    return [{"code": k, "name": v} for k, v in ITR_FORM_TYPES.items()]


@router.post("/calculate")
async def calculate_tax(req: TaxCalcRequest):
    return calculate_income_tax(
        gross_income=req.gross_income,
        deductions_80c=req.deductions_80c,
        deductions_80d=req.deductions_80d,
        deductions_80g=req.deductions_80g,
        deductions_80e=req.deductions_80e,
        hra_exemption=req.hra_exemption,
        lta_exemption=req.lta_exemption,
        other_exemptions=req.other_exemptions,
        old_regime=req.old_regime,
        is_senior=req.is_senior,
        tds_credited=req.tds_credited,
        advance_tax_paid=req.advance_tax_paid,
    )


@router.get("/advance-tax/schedule")
async def advance_tax_schedule(
    financial_year: str = Query(...),
):
    return get_advance_tax_schedule(financial_year)


@router.get("/filings", response_model=list[ItrFilingResponse])
async def list_itr_filings(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(ItrFiling).join(Client, ItrFiling.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(ItrFiling.client_id == client_id)
    query = query.order_by(ItrFiling.financial_year.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/filings", response_model=ItrFilingResponse, status_code=status.HTTP_201_CREATED)
async def create_itr_filing(
    req: ItrFilingCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    assessment_year = get_assessment_year(req.financial_year)
    due_date = req.due_date or date.fromisoformat(get_itr_due_date(req.form_type, req.financial_year))

    filing = ItrFiling(
        client_id=req.client_id,
        assessment_year=assessment_year,
        financial_year=req.financial_year,
        form_type=req.form_type,
        due_date=due_date,
        assigned_to=req.assigned_to,
        gross_income=req.gross_income,
    )
    db.add(filing)
    await db.commit()
    await db.refresh(filing)
    return filing


@router.put("/filings/{filing_id}", response_model=ItrFilingResponse)
async def update_itr_filing(
    filing_id: uuid.UUID,
    req: ItrFilingUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    filing = await db.get(ItrFiling, filing_id)
    if not filing:
        raise HTTPException(status_code=404, detail="ITR filing not found")
    client = await db.get(Client, filing.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="ITR filing not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(filing, field, value)
    await db.commit()
    await db.refresh(filing)
    return filing


@router.get("/advance-tax", response_model=list[AdvanceTaxResponse])
async def list_advance_tax(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(AdvanceTaxInstallment).join(Client, AdvanceTaxInstallment.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(AdvanceTaxInstallment.client_id == client_id)
    query = query.order_by(AdvanceTaxInstallment.installment_no)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/mca", response_model=list[McaFilingResponse])
async def list_mca_filings(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(McaFiling).join(Client, McaFiling.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(McaFiling.client_id == client_id)
    query = query.order_by(McaFiling.financial_year.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/mca", response_model=McaFilingResponse, status_code=status.HTTP_201_CREATED)
async def create_mca_filing(
    req: McaFilingCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    filing = McaFiling(**req.model_dump())
    db.add(filing)
    await db.commit()
    await db.refresh(filing)
    return filing


@router.get("/notices", response_model=list[IncomeTaxNoticeResponse])
async def list_income_tax_notices(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(IncomeTaxNotice).join(Client, IncomeTaxNotice.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(IncomeTaxNotice.client_id == client_id)
    query = query.order_by(IncomeTaxNotice.issue_date.desc())
    result = await db.execute(query)
    return result.scalars().all()
