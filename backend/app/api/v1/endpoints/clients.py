import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client, Task, TaskList
from app.models.bank import BankTransaction, BankConnection, JournalEntry
from app.models.organization import User
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientDetailResponse,
    ClientDashboardResponse,
)

router = APIRouter()


@router.get("/", response_model=list[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(Client).where(Client.org_id == user.org_id)
    if status_filter:
        query = query.where(Client.status == status_filter)
    query = query.order_by(Client.name).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    clients = result.scalars().all()

    responses = []
    for client in clients:
        task_count_result = await db.execute(
            select(func.count(Task.id))
            .join(TaskList, TaskList.id == Task.task_list_id)
            .where(TaskList.client_id == client.id)
        )
        task_count = task_count_result.scalar() or 0
        responses.append(ClientResponse(
            id=client.id,
            org_id=client.org_id,
            name=client.name,
            entity_type=client.entity_type,
            status=client.status,
            properties=client.properties,
            close_day=client.close_day,
            task_count=task_count,
            created_at=client.created_at,
            updated_at=client.updated_at,
        ))
    return responses


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    req: ClientCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = Client(
        org_id=user.org_id,
        name=req.name,
        entity_type=req.entity_type,
        status=req.status,
        properties=req.properties,
        close_day=req.close_day,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientResponse(
        id=client.id,
        org_id=client.org_id,
        name=client.name,
        entity_type=client.entity_type,
        status=client.status,
        properties=client.properties,
        close_day=client.close_day,
        task_count=0,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get("/{client_id}", response_model=ClientDetailResponse)
async def get_client(
    client_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    task_lists_result = await db.execute(
        select(TaskList).where(TaskList.client_id == client.id).order_by(TaskList.sort_order)
    )
    task_lists = task_lists_result.scalars().all()

    task_count_result = await db.execute(
        select(func.count(Task.id))
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(TaskList.client_id == client.id)
    )
    total_tasks = task_count_result.scalar() or 0

    open_tasks_result = await db.execute(
        select(func.count(Task.id))
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(TaskList.client_id == client.id, Task.status == "todo")
    )
    open_tasks = open_tasks_result.scalar() or 0

    done_tasks_result = await db.execute(
        select(func.count(Task.id))
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(TaskList.client_id == client.id, Task.status == "done")
    )
    done_tasks = done_tasks_result.scalar() or 0

    in_progress_result = await db.execute(
        select(func.count(Task.id))
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(TaskList.client_id == client.id, Task.status == "in_progress")
    )
    in_progress = in_progress_result.scalar() or 0

    return ClientDetailResponse(
        id=client.id,
        org_id=client.org_id,
        name=client.name,
        entity_type=client.entity_type,
        status=client.status,
        properties=client.properties,
        close_day=client.close_day,
        task_count=total_tasks,
        created_at=client.created_at,
        updated_at=client.updated_at,
        task_lists=[{"id": tl.id, "name": tl.name} for tl in task_lists],
        open_tasks=open_tasks,
        completed_tasks=done_tasks,
        in_progress_tasks=in_progress,
    )


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    req: ClientUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)

    task_count_result = await db.execute(
        select(func.count(Task.id))
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(TaskList.client_id == client.id)
    )
    task_count = task_count_result.scalar() or 0

    return ClientResponse(
        id=client.id,
        org_id=client.org_id,
        name=client.name,
        entity_type=client.entity_type,
        status=client.status,
        properties=client.properties,
        close_day=client.close_day,
        task_count=task_count,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")
    client.status = "inactive"
    await db.commit()


@router.get("/{client_id}/dashboard", response_model=ClientDashboardResponse)
async def client_dashboard(
    client_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    total = 0
    done = 0
    todo = 0
    in_progress = 0
    in_review = 0

    statuses = ["todo", "in_progress", "review", "done"]
    for s in statuses:
        count_result = await db.execute(
            select(func.count(Task.id))
            .join(TaskList, TaskList.id == Task.task_list_id)
            .where(TaskList.client_id == client.id, Task.status == s)
        )
        count = count_result.scalar() or 0
        total += count
        if s == "done":
            done = count
        elif s == "todo":
            todo = count
        elif s == "in_progress":
            in_progress = count
        elif s == "review":
            in_review = count

    completion_rate = (done / total * 100) if total > 0 else 0.0

    upcoming_result = await db.execute(
        select(Task)
        .join(TaskList, TaskList.id == Task.task_list_id)
        .where(
            TaskList.client_id == client.id,
            Task.status != "done",
            Task.due_date.isnot(None),
        )
        .order_by(Task.due_date.asc())
        .limit(5)
    )
    upcoming = [{"id": t.id, "name": t.name, "due_date": str(t.due_date), "status": t.status} for t in upcoming_result.scalars().all()]

    bank_txn_count = await db.execute(
        select(func.count(BankTransaction.id))
        .join(BankConnection, BankConnection.id == BankTransaction.bank_connection_id)
        .where(BankConnection.client_id == client.id)
    )
    bank_txn = bank_txn_count.scalar() or 0

    je_count = await db.execute(
        select(func.count(JournalEntry.id))
        .where(JournalEntry.client_id == client.id)
    )
    je = je_count.scalar() or 0

    return ClientDashboardResponse(
        total_tasks=total,
        completed_tasks=done,
        open_tasks=todo,
        in_progress_tasks=in_progress,
        in_review_tasks=in_review,
        completion_rate=round(completion_rate, 1),
        bank_transaction_count=bank_txn,
        journal_entry_count=je,
        upcoming_deadlines=upcoming,
    )
