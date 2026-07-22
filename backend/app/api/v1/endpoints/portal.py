import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.misc import PortalMessage, PortalDocument
from app.models.organization import User
from app.schemas.portal import (
    PortalMessageCreate,
    PortalMessageResponse,
    PortalDocumentResponse,
    PortalDocumentUpload,
    BrandingUpdate,
    BrandingResponse,
)

router = APIRouter()

branding_store: dict = {}


@router.get("/messages", response_model=list[PortalMessageResponse])
async def list_messages(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(PortalMessage).where(PortalMessage.org_id == user.org_id)
    if client_id:
        query = query.where(PortalMessage.client_id == client_id)
    query = query.order_by(PortalMessage.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/messages", response_model=PortalMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    req: PortalMessageCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    message = PortalMessage(
        client_id=req.client_id,
        org_id=user.org_id,
        sender_type=req.sender_type,
        sender_id=user_id,
        content=req.content,
        message_type=req.message_type,
        related_transaction_id=req.related_transaction_id,
        attachment_url=req.attachment_url,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.put("/messages/{message_id}/read", response_model=PortalMessageResponse)
async def mark_message_read(
    message_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    message = await db.get(PortalMessage, message_id)
    if not message or message.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Message not found")
    message.is_read = True
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/documents", response_model=list[PortalDocumentResponse])
async def list_documents(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(PortalDocument).where(PortalDocument.org_id == user.org_id)
    if client_id:
        query = query.where(PortalDocument.client_id == client_id)
    query = query.order_by(PortalDocument.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/documents", response_model=PortalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    req: PortalDocumentUpload,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    doc = PortalDocument(
        client_id=req.client_id,
        org_id=user.org_id,
        uploaded_by=req.uploaded_by,
        user_id=user_id,
        file_url=req.file_url,
        file_name=req.file_name,
        doc_type=req.doc_type,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/branding", response_model=BrandingResponse)
async def get_branding(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return BrandingResponse(**branding_store.get(str(user_id), {}))


@router.put("/branding", response_model=BrandingResponse)
async def update_branding(
    req: BrandingUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    branding_store[str(user_id)] = req.model_dump(exclude_unset=True)
    return BrandingResponse(**branding_store[str(user_id)])
