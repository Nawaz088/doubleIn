import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.misc import Integration, SyncLog
from app.services.token_crypto import encrypt_token, decrypt_token

QBO_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
QBO_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QBO_API_BASE = "https://quickbooks.api.intuit.com/v3/company"


async def get_qbo_auth_url(state: str) -> str:
    params = {
        "client_id": settings.QBO_CLIENT_ID,
        "redirect_uri": f"{settings.MAGIC_LINK_BASE_URL}/api/v1/integrations/qbo/callback",
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{QBO_AUTH_URL}?{query}"


async def exchange_qbo_code(code: str, realm_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            QBO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{settings.MAGIC_LINK_BASE_URL}/api/v1/integrations/qbo/callback",
            },
            auth=(settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET),
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_qbo_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            QBO_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(settings.QBO_CLIENT_ID, settings.QBO_CLIENT_SECRET),
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


async def qbo_api_request(
    integration: Integration,
    method: str,
    endpoint: str,
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
) -> dict:
    access_token = decrypt_token(integration.access_token)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    url = f"{QBO_API_BASE}/{integration.realm_id}/{endpoint}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method, url, headers=headers, params=params, json=json_body, timeout=30
        )
        resp.raise_for_status()
        return resp.json()


async def create_integration(
    db: AsyncSession,
    org_id: uuid.UUID,
    provider: str,
    access_token: str,
    refresh_token: str,
    realm_id: Optional[str] = None,
    token_expires_at: Optional[datetime] = None,
) -> Integration:
    integration = Integration(
        org_id=org_id,
        provider=provider,
        access_token=encrypt_token(access_token),
        refresh_token=encrypt_token(refresh_token) if refresh_token else None,
        realm_id=realm_id,
        token_expires_at=token_expires_at or (datetime.now(timezone.utc) + timedelta(days=100)),
        is_active=True,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


async def create_sync_log(
    db: AsyncSession,
    integration_id: uuid.UUID,
    entity_type: str,
    status: str = "running",
    records_synced: int = 0,
    error_message: Optional[str] = None,
) -> SyncLog:
    log = SyncLog(
        integration_id=integration_id,
        entity_type=entity_type,
        status=status,
        records_synced=records_synced,
        error_message=error_message,
        started_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
