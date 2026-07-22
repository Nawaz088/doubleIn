import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.receipts import Receipt
from app.models.organization import User
from app.schemas.receipts import (
    ReceiptResponse,
    ReceiptUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ReceiptResponse])
async def list_receipts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(Receipt).join(Client, Receipt.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(Receipt.client_id == client_id)
    if status_filter:
        query = query.where(Receipt.status == status_filter)
    query = query.order_by(Receipt.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    file_url: str,
    file_name: str,
    client_id: uuid.UUID,
    upload_method: str = "manual",
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    receipt = Receipt(
        client_id=client_id,
        upload_method=upload_method,
        file_url=file_url,
        file_name=file_name,
        status="processing",
    )
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)

    from app.services.ocr_engine import process_receipt_ocr
    try:
        await process_receipt_ocr(db, receipt)
    except Exception:
        receipt.status = "processing"

    await db.commit()
    await db.refresh(receipt)
    return receipt


@router.post("/{receipt_id}/reprocess", response_model=ReceiptResponse)
async def reprocess_receipt_ocr(
    receipt_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.ocr_engine import process_receipt_ocr

    user = await db.get(User, user_id)
    receipt = await db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    client = await db.get(Client, receipt.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Receipt not found")

    extracted = await process_receipt_ocr(db, receipt)
    return receipt


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    receipt = await db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    client = await db.get(Client, receipt.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: uuid.UUID,
    req: ReceiptUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    receipt = await db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    client = await db.get(Client, receipt.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Receipt not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(receipt, field, value)
    await db.commit()
    await db.refresh(receipt)
    return receipt


@router.post("/{receipt_id}/post", response_model=ReceiptResponse)
async def post_receipt(
    receipt_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    receipt = await db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    client = await db.get(Client, receipt.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Receipt not found")
    receipt.status = "posted"
    receipt.posted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(receipt)
    return receipt
