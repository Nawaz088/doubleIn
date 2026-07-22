import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.bank import BankConnection, BankTransaction, ClassificationRule
from app.models.organization import User
from app.schemas.bank import (
    BankConnectionCreate,
    BankConnectionResponse,
    BankTransactionResponse,
    BankTransactionUpdate,
    BulkActionRequest,
    ClassificationRuleCreate,
    ClassificationRuleUpdate,
    ClassificationRuleResponse,
)

router = APIRouter()


@router.get("/connections", response_model=list[BankConnectionResponse])
async def list_connections(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(BankConnection).join(Client, BankConnection.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(BankConnection.client_id == client_id)
    query = query.order_by(BankConnection.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/connections", response_model=BankConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    req: BankConnectionCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")
    conn = BankConnection(
        client_id=req.client_id,
        provider=req.provider,
        external_account_id=req.external_account_id,
        account_name=req.account_name,
        account_type=req.account_type,
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return conn


@router.post("/connections/sync", response_model=dict)
async def trigger_sync(
    connection_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    conn = await db.get(BankConnection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    client = await db.get(Client, conn.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Connection not found")
    conn.last_synced_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Sync initiated", "connection_id": str(connection_id)}


@router.get("/transactions", response_model=list[BankTransactionResponse])
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    classification: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(BankTransaction).join(
        BankConnection, BankTransaction.bank_connection_id == BankConnection.id
    ).join(Client, BankConnection.client_id == Client.id).where(Client.org_id == user.org_id)

    if client_id:
        query = query.where(BankConnection.client_id == client_id)
    if status_filter:
        query = query.where(BankTransaction.status == status_filter)
    if classification:
        query = query.where(BankTransaction.classification_tier == classification)
    if date_from:
        query = query.where(BankTransaction.date >= date_from)
    if date_to:
        query = query.where(BankTransaction.date <= date_to)

    query = query.order_by(BankTransaction.date.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/transactions/{transaction_id}", response_model=BankTransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    req: BankTransactionUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    txn = await db.get(BankTransaction, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    conn = await db.get(BankConnection, txn.bank_connection_id)
    client = await db.get(Client, conn.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    await db.commit()
    await db.refresh(txn)
    return txn


@router.post("/transactions/bulk", response_model=dict)
async def bulk_update_transactions(
    req: BulkActionRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    updated = 0
    for txn_id in req.transaction_ids:
        txn = await db.get(BankTransaction, txn_id)
        if not txn:
            continue
        conn = await db.get(BankConnection, txn.bank_connection_id)
        client = await db.get(Client, conn.client_id)
        if not client or client.org_id != user.org_id:
            continue
        if req.action == "approve":
            txn.status = "posted"
        elif req.action == "classify" and req.value:
            txn.classification_tier = req.value
        updated += 1
    await db.commit()
    return {"updated": updated, "action": req.action}


@router.get("/rules", response_model=list[ClassificationRuleResponse])
async def list_rules(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(ClassificationRule).join(Client, ClassificationRule.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(ClassificationRule.client_id == client_id)
    query = query.order_by(ClassificationRule.priority)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/rules", response_model=ClassificationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    req: ClassificationRuleCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")
    rule = ClassificationRule(
        client_id=req.client_id,
        conditions=req.conditions,
        actions=req.actions,
        priority=req.priority,
        is_active=req.is_active,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=ClassificationRuleResponse)
async def update_rule(
    rule_id: uuid.UUID,
    req: ClassificationRuleUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    rule = await db.get(ClassificationRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    client = await db.get(Client, rule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    rule = await db.get(ClassificationRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    client = await db.get(Client, rule.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = False
    await db.commit()
