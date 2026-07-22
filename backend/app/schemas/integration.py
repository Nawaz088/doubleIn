import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IntegrationResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    provider: str
    realm_id: Optional[str] = None
    is_active: bool
    last_sync_at: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationConnect(BaseModel):
    provider: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    realm_id: Optional[str] = None


class SyncLogResponse(BaseModel):
    id: uuid.UUID
    integration_id: uuid.UUID
    entity_type: str
    status: str
    records_synced: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
