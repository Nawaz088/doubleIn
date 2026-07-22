import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.misc import Integration, SyncLog
from app.services.token_crypto import encrypt_token

XERO_AUTH_URL = "https://login.xero.com/identity/connect/authorize"
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_API_BASE = "https://api.xero.com/api.xro/2.0"


async def get_xero_auth_url(state: str) -> str:
    params = {
        "client_id": settings.XERO_CLIENT_ID,
        "redirect_uri": f"{settings.MAGIC_LINK_BASE_URL}/api/v1/integrations/xero/callback",
        "response_type": "code",
        "scope": "openid profile email accounting.transactions accounting.settings",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{XERO_AUTH_URL}?{query}"


async def exchange_xero_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            XERO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{settings.MAGIC_LINK_BASE_URL}/api/v1/integrations/xero/callback",
            },
            auth=(settings.XERO_CLIENT_ID, settings.XERO_CLIENT_SECRET),
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


async def xero_api_request(
    integration: Integration,
    method: str,
    endpoint: str,
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
) -> dict:
    from app.services.token_crypto import decrypt_token
    access_token = decrypt_token(integration.access_token)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "xero-tenant-id": integration.realm_id or "",
    }
    url = f"{XERO_API_BASE}/{endpoint}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method, url, headers=headers, params=params, json=json_body, timeout=30
        )
        resp.raise_for_status()
        return resp.json()
