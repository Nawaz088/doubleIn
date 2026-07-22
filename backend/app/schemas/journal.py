import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class JournalEntryLineCreate(BaseModel):
    account_name: str
    account_external_id: Optional[str] = None
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    description: Optional[str] = None
    class_: Optional[str] = None
    location: Optional[str] = None


class JournalEntryLineResponse(BaseModel):
    id: uuid.UUID
    journal_entry_id: uuid.UUID
    account_name: str
    account_external_id: Optional[str] = None
    debit_amount: Decimal
    credit_amount: Decimal
    description: Optional[str] = None
    class_: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryCreate(BaseModel):
    client_id: uuid.UUID
    description: Optional[str] = None
    date: date
    source: str = "manual"
    lines: list[JournalEntryLineCreate]


class JournalEntryUpdate(BaseModel):
    description: Optional[str] = None
    date: Optional[date] = None
    source: Optional[str] = None
    status: Optional[str] = None


class JournalEntryResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    user_id: uuid.UUID
    description: Optional[str] = None
    date: date
    source: str
    status: str
    external_id: Optional[str] = None
    posted_at: Optional[datetime] = None
    lines_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryDetailResponse(JournalEntryResponse):
    lines: list[JournalEntryLineResponse] = []


class PostResponse(BaseModel):
    status: str
    external_id: Optional[str] = None
