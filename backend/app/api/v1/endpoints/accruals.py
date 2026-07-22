import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.receipts import AccrualSchedule, AccrualEntry
from app.models.organization import User
from app.schemas.receipts import (
    AccrualScheduleCreate,
    AccrualScheduleUpdate,
    AccrualScheduleResponse,
    AccrualScheduleDetailResponse,
    AccrualEntryResponse,
    GenerateEntriesRequest,
)

router = APIRouter()


@router.get("/", response_model=list[AccrualScheduleResponse])
async def list_schedules(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(AccrualSchedule).join(Client, AccrualSchedule.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(AccrualSchedule.client_id == client_id)
    query = query.order_by(AccrualSchedule.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=AccrualScheduleDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    req: AccrualScheduleCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    schedule = AccrualSchedule(
        client_id=req.client_id,
        name=req.name,
        type=req.type,
        total_amount=req.total_amount,
        start_date=req.start_date,
        end_date=req.end_date,
        recognition_method=req.recognition_method,
        journal_entry_template=req.journal_entry_template,
        status=req.status,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return AccrualScheduleDetailResponse(
        id=schedule.id, client_id=schedule.client_id, name=schedule.name,
        type=schedule.type, total_amount=schedule.total_amount,
        start_date=schedule.start_date, end_date=schedule.end_date,
        recognition_method=schedule.recognition_method,
        journal_entry_template=schedule.journal_entry_template,
        status=schedule.status, created_at=schedule.created_at, updated_at=schedule.updated_at,
        entries=[],
    )


@router.get("/{schedule_id}", response_model=AccrualScheduleDetailResponse)
async def get_schedule(
    schedule_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    schedule = await db.get(AccrualSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")
    client = await db.get(Client, schedule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")

    entries_result = await db.execute(
        select(AccrualEntry).where(AccrualEntry.schedule_id == schedule.id).order_by(AccrualEntry.period_date)
    )
    entries = [
        AccrualEntryResponse(
            id=e.id, schedule_id=e.schedule_id, period_date=e.period_date,
            recognized_amount=e.recognized_amount, journal_entry_id=e.journal_entry_id,
            status=e.status, posted_at=e.posted_at, created_at=e.created_at, updated_at=e.updated_at,
        ) for e in entries_result.scalars().all()
    ]
    return AccrualScheduleDetailResponse(
        id=schedule.id, client_id=schedule.client_id, name=schedule.name,
        type=schedule.type, total_amount=schedule.total_amount,
        start_date=schedule.start_date, end_date=schedule.end_date,
        recognition_method=schedule.recognition_method,
        journal_entry_template=schedule.journal_entry_template,
        status=schedule.status, created_at=schedule.created_at, updated_at=schedule.updated_at,
        entries=entries,
    )


@router.put("/{schedule_id}", response_model=AccrualScheduleDetailResponse)
async def update_schedule(
    schedule_id: uuid.UUID,
    req: AccrualScheduleUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    schedule = await db.get(AccrualSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")
    client = await db.get(Client, schedule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await db.commit()
    await db.refresh(schedule)

    entries_result = await db.execute(
        select(AccrualEntry).where(AccrualEntry.schedule_id == schedule.id).order_by(AccrualEntry.period_date)
    )
    entries = [
        AccrualEntryResponse(
            id=e.id, schedule_id=e.schedule_id, period_date=e.period_date,
            recognized_amount=e.recognized_amount, journal_entry_id=e.journal_entry_id,
            status=e.status, posted_at=e.posted_at, created_at=e.created_at, updated_at=e.updated_at,
        ) for e in entries_result.scalars().all()
    ]
    return AccrualScheduleDetailResponse(
        id=schedule.id, client_id=schedule.client_id, name=schedule.name,
        type=schedule.type, total_amount=schedule.total_amount,
        start_date=schedule.start_date, end_date=schedule.end_date,
        recognition_method=schedule.recognition_method,
        journal_entry_template=schedule.journal_entry_template,
        status=schedule.status, created_at=schedule.created_at, updated_at=schedule.updated_at,
        entries=entries,
    )


@router.post("/{schedule_id}/entries/generate", response_model=dict)
async def generate_entries(
    schedule_id: uuid.UUID,
    req: GenerateEntriesRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    schedule = await db.get(AccrualSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")
    client = await db.get(Client, schedule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Accrual schedule not found")

    amount_per_period = schedule.total_amount / req.periods
    created = 0
    from datetime import timedelta

    for i in range(req.periods):
        period_date = schedule.start_date + timedelta(days=30 * i)
        if schedule.end_date and period_date > schedule.end_date:
            break

        existing = await db.execute(
            select(AccrualEntry).where(
                AccrualEntry.schedule_id == schedule_id,
                AccrualEntry.period_date == period_date,
            )
        )
        if existing.scalar_one_or_none():
            continue

        entry = AccrualEntry(
            schedule_id=schedule_id,
            period_date=period_date,
            recognized_amount=float(amount_per_period),
        )
        db.add(entry)
        created += 1

    await db.commit()
    return {"message": f"Generated {created} entries", "schedule_id": str(schedule_id)}


@router.post("/entries/{entry_id}/post", response_model=AccrualEntryResponse)
async def post_accrual_entry(
    entry_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    entry = await db.get(AccrualEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Accrual entry not found")
    schedule = await db.get(AccrualSchedule, entry.schedule_id)
    client = await db.get(Client, schedule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Accrual entry not found")

    entry.status = "posted"
    entry.posted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(entry)
    return entry
