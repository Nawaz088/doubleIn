import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.organization import User
from app.models.accounting_india import IndianChartOfAccount, IndianFinancialYear
from app.services.india_utils import (
    INDIAN_ENTITY_TYPES, flatten_schedule_iii,
    get_current_fy, get_fy_start_end, format_inr_indian,
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class CoaCreate(BaseModel):
    code: str
    name: str
    type: str
    subtype: Optional[str] = None
    schedule: Optional[str] = None
    is_schedule_iii: bool = False
    parent_code: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class CoaUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class CoaResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    code: str
    name: str
    type: str
    subtype: Optional[str] = None
    schedule: Optional[str] = None
    is_schedule_iii: bool
    parent_code: Optional[str] = None
    is_active: bool
    description: Optional[str] = None
    sort_order: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class FinancialYearResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    fy: str
    start_date: str
    end_date: str
    is_current: bool
    is_locked: bool
    previous_fy: Optional[str] = None

    model_config = {"from_attributes": True}


class EntityTypeResponse(BaseModel):
    value: str
    label: str


@router.get("/entity-types", response_model=list[EntityTypeResponse])
async def list_entity_types():
    return [{"value": et[0], "label": et[1]} for et in INDIAN_ENTITY_TYPES]


@router.get("/chart-of-accounts", response_model=list[CoaResponse])
async def list_chart_of_accounts(
    type_filter: str | None = Query(None, alias="type"),
    schedule: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(IndianChartOfAccount).where(IndianChartOfAccount.org_id == user.org_id)
    if type_filter:
        query = query.where(IndianChartOfAccount.type == type_filter)
    if schedule:
        query = query.where(IndianChartOfAccount.schedule == schedule)
    query = query.order_by(IndianChartOfAccount.code)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/chart-of-accounts/seed", status_code=status.HTTP_201_CREATED)
async def seed_schedule_iii(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    existing = await db.execute(
        select(IndianChartOfAccount).where(
            IndianChartOfAccount.org_id == user.org_id,
            IndianChartOfAccount.is_schedule_iii == True,
        )
    )
    if existing.scalars().first():
        return {"message": "Schedule III accounts already seeded"}

    accounts = flatten_schedule_iii()
    for acc in accounts:
        coa = IndianChartOfAccount(
            org_id=user.org_id,
            code=acc["code"],
            name=acc["name"],
            type=acc["type"],
            subtype=acc["subtype"],
            schedule=acc["schedule"],
            is_schedule_iii=acc["is_schedule_iii"],
        )
        db.add(coa)
    await db.commit()
    return {"message": f"Seeded {len(accounts)} Schedule III accounts"}


@router.put("/chart-of-accounts/{account_id}", response_model=CoaResponse)
async def update_chart_of_account(
    account_id: uuid.UUID,
    req: CoaUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    account = await db.get(IndianChartOfAccount, account_id)
    if not account or account.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Account not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/financial-years", response_model=list[FinancialYearResponse])
async def list_financial_years(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(IndianFinancialYear).where(IndianFinancialYear.org_id == user.org_id).order_by(IndianFinancialYear.fy.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/financial-years/setup", status_code=status.HTTP_201_CREATED)
async def setup_financial_years(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    existing = await db.execute(
        select(IndianFinancialYear).where(IndianFinancialYear.org_id == user.org_id)
    )
    if existing.scalars().first():
        return {"message": "Financial years already set up"}

    current_fy = get_current_fy()
    fy_start, fy_end = get_fy_start_end(current_fy)

    fy = IndianFinancialYear(
        org_id=user.org_id,
        fy=current_fy,
        start_date=fy_start.isoformat(),
        end_date=fy_end.isoformat(),
        is_current=True,
    )
    db.add(fy)
    await db.commit()
    return {"message": f"Financial year {current_fy} set up", "fy": current_fy}


@router.get("/fy/current")
async def get_current_fy_endpoint(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(IndianFinancialYear).where(
            IndianFinancialYear.org_id == user.org_id,
            IndianFinancialYear.is_current == True,
        )
    )
    fy = result.scalar_one_or_none()
    if not fy:
        return {"fy": get_current_fy()}
    return {"fy": fy.fy, "start_date": fy.start_date, "end_date": fy.end_date}
