import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Task, TaskList, Client
from app.models.misc import EmailMessage, EmailTaskLink
from app.models.organization import User
from app.schemas.inbox import EmailMessageResponse, EmailMessageDetailResponse

router = APIRouter()


@router.get("/", response_model=list[EmailMessageResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(EmailMessage).where(
        EmailMessage.org_id == user.org_id,
        EmailMessage.is_deleted == False,
    )
    if client_id:
        query = query.where(EmailMessage.client_id == client_id)
    query = query.order_by(EmailMessage.received_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{email_id}", response_model=EmailMessageDetailResponse)
async def get_email(
    email_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    email = await db.get(EmailMessage, email_id)
    if not email or email.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/{email_id}/convert-task", response_model=dict, status_code=status.HTTP_201_CREATED)
async def convert_email_to_task(
    email_id: uuid.UUID,
    task_list_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    email = await db.get(EmailMessage, email_id)
    if not email or email.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Email not found")

    tl = await db.get(TaskList, task_list_id)
    if not tl:
        raise HTTPException(status_code=404, detail="Task list not found")
    client = await db.get(Client, tl.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Task list not found")

    task = Task(
        task_list_id=task_list_id,
        name=f"[Email] {email.subject}",
        description=email.body_text[:1000] if email.body_text else None,
        status="todo",
    )
    db.add(task)
    await db.flush()

    link = EmailTaskLink(
        email_id=email_id,
        task_id=task.id,
    )
    db.add(link)
    await db.commit()

    return {"task_id": str(task.id), "email_id": str(email.id)}


@router.put("/{email_id}/read", response_model=EmailMessageResponse)
async def mark_email_read(
    email_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    email = await db.get(EmailMessage, email_id)
    if not email or email.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Email not found")
    email.is_read = True
    await db.commit()
    await db.refresh(email)
    return email
