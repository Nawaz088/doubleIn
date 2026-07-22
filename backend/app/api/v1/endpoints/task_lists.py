import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Task, TaskList, Client
from app.models.misc import TaskComment, TaskAttachment
from app.models.organization import User
from app.schemas.task import (
    TaskListCreate,
    TaskListUpdate,
    TaskListResponse,
    TaskListReorder,
    TaskResponse,
)

router = APIRouter()


@router.get("/", response_model=list[TaskListResponse])
async def list_task_lists(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TaskList).join(Client, TaskList.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TaskList.client_id == client_id)
    query = query.order_by(TaskList.sort_order)
    result = await db.execute(query)
    task_lists = result.scalars().all()

    responses = []
    for tl in task_lists:
        tasks_result = await db.execute(
            select(Task).where(Task.task_list_id == tl.id, Task.parent_id.is_(None)).order_by(Task.sort_order)
        )
        tasks = []
        for task in tasks_result.scalars().all():
            cc = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)) or 0
            tasks.append(TaskResponse(
                id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
                name=task.name, description=task.description, assignee_id=task.assignee_id,
                due_date=task.due_date, priority=task.priority, status=task.status,
                tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
                sort_order=task.sort_order, completed_at=task.completed_at,
                comments_count=cc, created_at=task.created_at, updated_at=task.updated_at,
            ))
        responses.append(TaskListResponse(
            id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
            is_template=tl.is_template, tasks=tasks, created_at=tl.created_at, updated_at=tl.updated_at,
        ))
    return responses


@router.post("/", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
async def create_task_list(
    req: TaskListCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    tl = TaskList(
        client_id=req.client_id,
        name=req.name,
        sort_order=req.sort_order,
        is_template=req.is_template,
    )
    db.add(tl)
    await db.commit()
    await db.refresh(tl)
    return TaskListResponse(
        id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
        is_template=tl.is_template, tasks=[], created_at=tl.created_at, updated_at=tl.updated_at,
    )


@router.get("/{task_list_id}", response_model=TaskListResponse)
async def get_task_list(
    task_list_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tl = await db.get(TaskList, task_list_id)
    if not tl:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, tl.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task list not found")

    tasks_result = await db.execute(
        select(Task).where(Task.task_list_id == tl.id).order_by(Task.sort_order)
    )
    tasks = []
    for task in tasks_result.scalars().all():
        cc = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)) or 0
        tasks.append(TaskResponse(
            id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
            name=task.name, description=task.description, assignee_id=task.assignee_id,
            due_date=task.due_date, priority=task.priority, status=task.status,
            tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
            sort_order=task.sort_order, completed_at=task.completed_at,
            comments_count=cc, created_at=task.created_at, updated_at=task.updated_at,
        ))
    return TaskListResponse(
        id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
        is_template=tl.is_template, tasks=tasks, created_at=tl.created_at, updated_at=tl.updated_at,
    )


@router.put("/{task_list_id}", response_model=TaskListResponse)
async def update_task_list(
    task_list_id: uuid.UUID,
    req: TaskListUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tl = await db.get(TaskList, task_list_id)
    if not tl:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, tl.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task list not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(tl, field, value)
    await db.commit()
    await db.refresh(tl)

    tasks_result = await db.execute(
        select(Task).where(Task.task_list_id == tl.id).order_by(Task.sort_order)
    )
    tasks = []
    for task in tasks_result.scalars().all():
        cc = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)) or 0
        tasks.append(TaskResponse(
            id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
            name=task.name, description=task.description, assignee_id=task.assignee_id,
            due_date=task.due_date, priority=task.priority, status=task.status,
            tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
            sort_order=task.sort_order, completed_at=task.completed_at,
            comments_count=cc, created_at=task.created_at, updated_at=task.updated_at,
        ))
    return TaskListResponse(
        id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
        is_template=tl.is_template, tasks=tasks, created_at=tl.created_at, updated_at=tl.updated_at,
    )


@router.delete("/{task_list_id}", status_code=204)
async def delete_task_list(
    task_list_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tl = await db.get(TaskList, task_list_id)
    if not tl:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, tl.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task list not found")

    child_tasks = await db.execute(select(Task).where(Task.parent_id.in_(
        select(Task.id).where(Task.task_list_id == task_list_id)
    )))
    for child in child_tasks.scalars().all():
        await db.execute(sa_delete(TaskComment).where(TaskComment.task_id == child.id))
        await db.execute(sa_delete(TaskAttachment).where(TaskAttachment.task_id == child.id))
    await db.execute(sa_delete(TaskComment).where(TaskComment.task_id.in_(
        select(Task.id).where(Task.task_list_id == task_list_id)
    )))
    await db.execute(sa_delete(TaskAttachment).where(TaskAttachment.task_id.in_(
        select(Task.id).where(Task.task_list_id == task_list_id)
    )))
    await db.execute(sa_delete(Task).where(Task.task_list_id == task_list_id))
    await db.delete(tl)
    await db.commit()


@router.put("/{task_list_id}/reorder", response_model=TaskListResponse)
async def reorder_tasks(
    task_list_id: uuid.UUID,
    req: TaskListReorder,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tl = await db.get(TaskList, task_list_id)
    if not tl:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, tl.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task list not found")

    for idx, task_id in enumerate(req.task_ids):
        task = await db.get(Task, task_id)
        if task and task.task_list_id == task_list_id:
            task.sort_order = idx
    await db.commit()

    tasks_result = await db.execute(
        select(Task).where(Task.task_list_id == tl.id).order_by(Task.sort_order)
    )
    tasks = []
    for task in tasks_result.scalars().all():
        cc = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)) or 0
        tasks.append(TaskResponse(
            id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
            name=task.name, description=task.description, assignee_id=task.assignee_id,
            due_date=task.due_date, priority=task.priority, status=task.status,
            tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
            sort_order=task.sort_order, completed_at=task.completed_at,
            comments_count=cc, created_at=task.created_at, updated_at=task.updated_at,
        ))
    return TaskListResponse(
        id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
        is_template=tl.is_template, tasks=tasks, created_at=tl.created_at, updated_at=tl.updated_at,
    )
