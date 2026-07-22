import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Task, TaskList, Client
from app.models.misc import TaskComment, TaskAttachment
from app.models.organization import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskAttachmentResponse,
    TaskListResponse,
)

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    assignee_id: uuid.UUID | None = Query(None),
    priority: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(Task).join(TaskList, Task.task_list_id == TaskList.id).join(
        Client, TaskList.client_id == Client.id
    ).where(Client.org_id == user.org_id)

    if client_id:
        query = query.where(Client.id == client_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if priority:
        query = query.where(Task.priority == priority)

    query = query.order_by(Task.sort_order, Task.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()

    responses = []
    for task in tasks:
        comment_count = await db.scalar(
            select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)
        ) or 0
        responses.append(TaskResponse(
            id=task.id,
            task_list_id=task.task_list_id,
            parent_id=task.parent_id,
            name=task.name,
            description=task.description,
            assignee_id=task.assignee_id,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
            tags=task.tags,
            is_recurring=task.is_recurring,
            recurring_schedule=task.recurring_schedule,
            sort_order=task.sort_order,
            completed_at=task.completed_at,
            comments_count=comment_count,
            created_at=task.created_at,
            updated_at=task.updated_at,
        ))
    return responses


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task_list = await db.get(TaskList, req.task_list_id)
    if not task_list:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    task = Task(
        task_list_id=req.task_list_id,
        parent_id=req.parent_id,
        name=req.name,
        description=req.description,
        assignee_id=req.assignee_id,
        due_date=req.due_date,
        priority=req.priority,
        status=req.status,
        tags=req.tags,
        is_recurring=req.is_recurring,
        recurring_schedule=req.recurring_schedule,
        sort_order=req.sort_order,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskResponse(
        id=task.id,
        task_list_id=task.task_list_id,
        parent_id=task.parent_id,
        name=task.name,
        description=task.description,
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        priority=task.priority,
        status=task.status,
        tags=task.tags,
        is_recurring=task.is_recurring,
        recurring_schedule=task.recurring_schedule,
        sort_order=task.sort_order,
        completed_at=task.completed_at,
        comments_count=0,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    comment_count = await db.scalar(
        select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)
    ) or 0

    comments_result = await db.execute(
        select(TaskComment).where(TaskComment.task_id == task.id).order_by(TaskComment.created_at)
    )
    comments = [
        TaskCommentResponse(
            id=c.id, task_id=c.task_id, user_id=c.user_id,
            content=c.content, attachment_url=c.attachment_url, created_at=c.created_at,
        )
        for c in comments_result.scalars().all()
    ]

    attachments_result = await db.execute(
        select(TaskAttachment).where(TaskAttachment.task_id == task.id).order_by(TaskAttachment.created_at)
    )
    attachments = [
        TaskAttachmentResponse(
            id=a.id, task_id=a.task_id, user_id=a.user_id,
            file_name=a.file_name, file_url=a.file_url, file_type=a.file_type, created_at=a.created_at,
        )
        for a in attachments_result.scalars().all()
    ]

    children_result = await db.execute(
        select(Task).where(Task.parent_id == task.id).order_by(Task.sort_order)
    )
    children = []
    for child in children_result.scalars().all():
        cc = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == child.id)) or 0
        children.append(TaskResponse(
            id=child.id, task_list_id=child.task_list_id, parent_id=child.parent_id,
            name=child.name, description=child.description, assignee_id=child.assignee_id,
            due_date=child.due_date, priority=child.priority, status=child.status,
            tags=child.tags, is_recurring=child.is_recurring, recurring_schedule=child.recurring_schedule,
            sort_order=child.sort_order, completed_at=child.completed_at, comments_count=cc,
            created_at=child.created_at, updated_at=child.updated_at,
        ))

    return TaskDetailResponse(
        id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
        name=task.name, description=task.description, assignee_id=task.assignee_id,
        due_date=task.due_date, priority=task.priority, status=task.status,
        tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
        sort_order=task.sort_order, completed_at=task.completed_at,
        comments_count=comment_count, created_at=task.created_at, updated_at=task.updated_at,
        comments=comments, attachments=attachments, children=children,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    req: TaskUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if req.status == "done" and task.status != "done":
        task.completed_at = datetime.now(timezone.utc)
    elif req.status and req.status != "done":
        task.completed_at = None

    for field, value in req.model_dump(exclude_unset=True).items():
        if field == "completed_at":
            continue
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)

    comment_count = await db.scalar(
        select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)
    ) or 0
    return TaskResponse(
        id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
        name=task.name, description=task.description, assignee_id=task.assignee_id,
        due_date=task.due_date, priority=task.priority, status=task.status,
        tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
        sort_order=task.sort_order, completed_at=task.completed_at,
        comments_count=comment_count, created_at=task.created_at, updated_at=task.updated_at,
    )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "done"
    task.completed_at = datetime.now(timezone.utc)
    await db.commit()


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=201)
async def add_task_comment(
    task_id: uuid.UUID,
    req: TaskCommentCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = TaskComment(
        task_id=task_id,
        user_id=user_id,
        content=req.content,
        attachment_url=req.attachment_url,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.post("/{task_id}/attachments", response_model=TaskAttachmentResponse, status_code=201)
async def create_task_attachment(
    task_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    attachment = TaskAttachment(
        task_id=task_id,
        user_id=user_id,
        file_name="placeholder.pdf",
        file_url=f"/uploads/{task_id}/placeholder.pdf",
        file_type="application/pdf",
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: uuid.UUID,
    assignee_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_list = await db.get(TaskList, task.task_list_id)
    client = await db.get(Client, task_list.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.assignee_id = assignee_id
    await db.commit()
    await db.refresh(task)

    comment_count = await db.scalar(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id)) or 0
    return TaskResponse(
        id=task.id, task_list_id=task.task_list_id, parent_id=task.parent_id,
        name=task.name, description=task.description, assignee_id=task.assignee_id,
        due_date=task.due_date, priority=task.priority, status=task.status,
        tags=task.tags, is_recurring=task.is_recurring, recurring_schedule=task.recurring_schedule,
        sort_order=task.sort_order, completed_at=task.completed_at,
        comments_count=comment_count, created_at=task.created_at, updated_at=task.updated_at,
    )


@router.get("/templates", response_model=list[TaskListResponse])
async def list_templates(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(TaskList)
        .join(Client, TaskList.client_id == Client.id)
        .where(Client.org_id == user.org_id, TaskList.is_template == True)
        .order_by(TaskList.name)
    )
    template_lists = result.scalars().all()

    responses = []
    for tl in template_lists:
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
        responses.append(TaskListResponse(
            id=tl.id, client_id=tl.client_id, name=tl.name, sort_order=tl.sort_order,
            is_template=tl.is_template, tasks=tasks, created_at=tl.created_at, updated_at=tl.updated_at,
        ))
    return responses
