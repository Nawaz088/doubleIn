import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.bank import JournalEntry, JournalEntryLine
from app.models.organization import User
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalEntryDetailResponse,
    JournalEntryLineCreate,
    JournalEntryLineResponse,
    PostResponse,
)

router = APIRouter()


@router.get("/", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(JournalEntry).join(Client, JournalEntry.client_id == Client.id).where(Client.org_id == user.org_id)

    if client_id:
        query = query.where(JournalEntry.client_id == client_id)
    if status_filter:
        query = query.where(JournalEntry.status == status_filter)
    if date_from:
        query = query.where(JournalEntry.date >= date_from)
    if date_to:
        query = query.where(JournalEntry.date <= date_to)

    query = query.order_by(JournalEntry.date.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    entries = result.scalars().all()

    responses = []
    for entry in entries:
        count_result = await db.execute(
            select(func.count(JournalEntryLine.id)).where(JournalEntryLine.journal_entry_id == entry.id)
        )
        lc = count_result.scalar() or 0
        responses.append(JournalEntryResponse(
            id=entry.id, client_id=entry.client_id, user_id=entry.user_id,
            description=entry.description, date=entry.date, source=entry.source,
            status=entry.status, external_id=entry.external_id, posted_at=entry.posted_at,
            lines_count=lc, created_at=entry.created_at, updated_at=entry.updated_at,
        ))
    return responses


@router.post("/", response_model=JournalEntryDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    req: JournalEntryCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    entry = JournalEntry(
        client_id=req.client_id,
        user_id=user_id,
        description=req.description,
        date=req.date,
        source=req.source,
        status="draft",
    )
    db.add(entry)
    await db.flush()

    lines = []
    for line_data in req.lines:
        line = JournalEntryLine(
            journal_entry_id=entry.id,
            account_name=line_data.account_name,
            account_external_id=line_data.account_external_id,
            debit_amount=line_data.debit_amount,
            credit_amount=line_data.credit_amount,
            description=line_data.description,
            class_=line_data.class_,
            location=line_data.location,
        )
        db.add(line)
        lines.append(line)

    await db.commit()
    await db.refresh(entry)
    for line in lines:
        await db.refresh(line)

    return JournalEntryDetailResponse(
        id=entry.id, client_id=entry.client_id, user_id=entry.user_id,
        description=entry.description, date=entry.date, source=entry.source,
        status=entry.status, external_id=entry.external_id, posted_at=entry.posted_at,
        lines_count=len(lines), created_at=entry.created_at, updated_at=entry.updated_at,
        lines=[
            JournalEntryLineResponse(
                id=l.id, journal_entry_id=l.journal_entry_id, account_name=l.account_name,
                account_external_id=l.account_external_id, debit_amount=l.debit_amount,
                credit_amount=l.credit_amount, description=l.description,
                class_=l.class_, location=l.location,
                created_at=l.created_at, updated_at=l.updated_at,
            ) for l in lines
        ],
    )


@router.get("/{entry_id}", response_model=JournalEntryDetailResponse)
async def get_journal_entry(
    entry_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    entry = await db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    client = await db.get(Client, entry.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    ll_result = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == entry.id).order_by(JournalEntryLine.created_at)
    )
    ll = ll_result.scalars().all()

    return JournalEntryDetailResponse(
        id=entry.id, client_id=entry.client_id, user_id=entry.user_id,
        description=entry.description, date=entry.date, source=entry.source,
        status=entry.status, external_id=entry.external_id, posted_at=entry.posted_at,
        lines_count=len(ll), created_at=entry.created_at, updated_at=entry.updated_at,
        lines=[
            JournalEntryLineResponse(
                id=l.id, journal_entry_id=l.journal_entry_id, account_name=l.account_name,
                account_external_id=l.account_external_id, debit_amount=l.debit_amount,
                credit_amount=l.credit_amount, description=l.description,
                class_=l.class_, location=l.location,
                created_at=l.created_at, updated_at=l.updated_at,
            ) for l in ll
        ],
    )


@router.put("/{entry_id}", response_model=JournalEntryDetailResponse)
async def update_journal_entry(
    entry_id: uuid.UUID,
    req: JournalEntryUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    entry = await db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    client = await db.get(Client, entry.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)

    ll_result = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == entry.id).order_by(JournalEntryLine.created_at)
    )
    ll = ll_result.scalars().all()

    return JournalEntryDetailResponse(
        id=entry.id, client_id=entry.client_id, user_id=entry.user_id,
        description=entry.description, date=entry.date, source=entry.source,
        status=entry.status, external_id=entry.external_id, posted_at=entry.posted_at,
        lines_count=len(ll), created_at=entry.created_at, updated_at=entry.updated_at,
        lines=[
            JournalEntryLineResponse(
                id=l.id, journal_entry_id=l.journal_entry_id, account_name=l.account_name,
                account_external_id=l.account_external_id, debit_amount=l.debit_amount,
                credit_amount=l.credit_amount, description=l.description,
                class_=l.class_, location=l.location,
                created_at=l.created_at, updated_at=l.updated_at,
            ) for l in ll
        ],
    )


@router.post("/{entry_id}/post", response_model=PostResponse)
async def post_journal_entry(
    entry_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    entry = await db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    client = await db.get(Client, entry.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    entry.status = "posted"
    entry.posted_at = datetime.now(timezone.utc)
    entry.external_id = f"posted-{entry.id}"
    await db.commit()
    return PostResponse(status="posted", external_id=entry.external_id)


@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    entry = await db.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if entry.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft entries can be deleted")
    client = await db.get(Client, entry.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    await db.delete(entry)
    await db.commit()
