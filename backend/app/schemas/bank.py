import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BankConnectionCreate(BaseModel):
    client_id: uuid.UUID
    provider: str
    external_account_id: str
    account_name: str
    account_type: Optional[str] = None


class BankConnectionResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    provider: str
    external_account_id: str
    account_name: str
    account_type: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BankTransactionResponse(BaseModel):
    id: uuid.UUID
    bank_connection_id: uuid.UUID
    external_id: str
    date: date
    amount: Decimal
    description: str
    vendor_name: Optional[str] = None
    category: Optional[str] = None
    status: str
    classification_tier: str
    matched_transaction_id: Optional[uuid.UUID] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BankTransactionUpdate(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None
    classification_tier: Optional[str] = None


class BulkActionRequest(BaseModel):
    transaction_ids: list[uuid.UUID]
    action: str
    value: Optional[str] = None


class ClassificationRuleCreate(BaseModel):
    client_id: uuid.UUID
    conditions: dict
    actions: dict
    priority: int = 0
    is_active: bool = True


class ClassificationRuleUpdate(BaseModel):
    conditions: Optional[dict] = None
    actions: Optional[dict] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class ClassificationRuleResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    conditions: dict
    actions: dict
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
