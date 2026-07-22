import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.misc import Integration, SyncLog
from app.models.organization import User
from app.schemas.integration import (
    IntegrationResponse,
    IntegrationConnect,
    SyncLogResponse,
)

router = APIRouter()


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(Integration).where(Integration.org_id == user.org_id).order_by(Integration.created_at.desc())
    )
    return result.scalars().all()


@router.get("/qbo/auth")
async def qbo_auth_url(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.integrations.qbo import get_qbo_auth_url
    import secrets
    state = secrets.token_urlsafe(32)
    url = await get_qbo_auth_url(state)
    return {"auth_url": url, "state": state}


@router.get("/qbo/callback")
async def qbo_callback(
    code: str = Query(...),
    realmId: str = Query(...),
    state: str = Query(...),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.integrations.qbo import exchange_qbo_code
    from app.services.integrations.qbo_sync import create_integration as create_qbo_integration

    tokens = await exchange_qbo_code(code, realmId)
    user = await db.get(User, user_id)

    integration = Integration(
        org_id=user.org_id,
        provider="qbo",
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        realm_id=realmId,
        token_expires_at=datetime.now(timezone.utc).replace(
            second=datetime.now(timezone.utc).second + tokens.get("expires_in", 3600)
        ),
        is_active=True,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return {"message": "QBO connected successfully", "integration_id": str(integration.id)}


@router.get("/xero/auth")
async def xero_auth_url(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.integrations.xero import get_xero_auth_url
    import secrets
    state = secrets.token_urlsafe(32)
    url = await get_xero_auth_url(state)
    return {"auth_url": url, "state": state}


@router.get("/xero/callback")
async def xero_callback(
    code: str = Query(...),
    state: str = Query(...),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.integrations.xero import exchange_xero_code

    tokens = await exchange_xero_code(code)
    user = await db.get(User, user_id)

    integration = Integration(
        org_id=user.org_id,
        provider="xero",
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        realm_id=tokens.get("xero_tenant_id"),
        token_expires_at=datetime.now(timezone.utc).replace(
            second=datetime.now(timezone.utc).second + tokens.get("expires_in", 1800)
        ),
        is_active=True,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return {"message": "Xero connected successfully", "integration_id": str(integration.id)}


@router.post("/connect", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def connect_integration(
    req: IntegrationConnect,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    integration = Integration(
        org_id=user.org_id,
        provider=req.provider,
        access_token=req.access_token,
        refresh_token=req.refresh_token,
        token_expires_at=req.token_expires_at,
        realm_id=req.realm_id,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.post("/{integration_id}/sync", response_model=dict)
async def trigger_sync(
    integration_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.integrations.qbo_sync import (
        sync_qbo_chart_of_accounts,
        sync_qbo_transactions,
        sync_qbo_vendors,
        sync_qbo_customers,
    )

    user = await db.get(User, user_id)
    integration = await db.get(Integration, integration_id)
    if not integration or integration.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Integration not found")

    sync_log = SyncLog(
        integration_id=integration_id,
        entity_type="full_sync",
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(sync_log)
    await db.flush()

    total_synced = 0
    error_msg = None

    try:
        if integration.provider == "qbo":
            accounts = await sync_qbo_chart_of_accounts(db, integration, uuid.uuid4())
            txns = await sync_qbo_transactions(db, integration, uuid.uuid4())
            vendors = await sync_qbo_vendors(db, integration, uuid.uuid4())
            customers = await sync_qbo_customers(db, integration, uuid.uuid4())
            total_synced = accounts + txns + vendors + customers

        integration.last_sync_at = datetime.now(timezone.utc)
        sync_log.status = "success"
        sync_log.records_synced = total_synced
    except Exception as e:
        sync_log.status = "error"
        error_msg = str(e)
        sync_log.error_message = error_msg

    sync_log.completed_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "message": "Sync completed" if sync_log.status == "success" else f"Sync failed: {error_msg}",
        "integration_id": str(integration_id),
        "records_synced": total_synced,
        "status": sync_log.status,
    }


@router.put("/{integration_id}/disconnect", response_model=IntegrationResponse)
async def disconnect_integration(
    integration_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    integration = await db.get(Integration, integration_id)
    if not integration or integration.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Integration not found")
    integration.is_active = False
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/{integration_id}/sync-logs", response_model=list[SyncLogResponse])
async def get_sync_logs(
    integration_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    integration = await db.get(Integration, integration_id)
    if not integration or integration.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Integration not found")

    result = await db.execute(
        select(SyncLog)
        .where(SyncLog.integration_id == integration_id)
        .order_by(SyncLog.started_at.desc())
    )
    return result.scalars().all()
