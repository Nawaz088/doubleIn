import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReceiptUploadResponse(BaseModel):
    id: uuid.UUID
    file_url: str
    file_name: str
    upload_method: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReceiptResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    upload_method: str
    file_url: str
    file_name: str
    ocr_text: Optional[str] = None
    extracted_data: Optional[dict] = None
    status: str
    matched_transaction_id: Optional[uuid.UUID] = None
    posted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReceiptUpdate(BaseModel):
    status: Optional[str] = None
    matched_transaction_id: Optional[uuid.UUID] = None
    extracted_data: Optional[dict] = None
    ocr_text: Optional[str] = None


class AccrualScheduleCreate(BaseModel):
    client_id: uuid.UUID
    name: str
    type: str
    total_amount: float
    start_date: date
    end_date: Optional[date] = None
    recognition_method: str = "straight_line"
    journal_entry_template: Optional[dict] = None
    status: str = "active"


class AccrualScheduleUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    total_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    recognition_method: Optional[str] = None
    journal_entry_template: Optional[dict] = None
    status: Optional[str] = None


class AccrualScheduleResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    type: str
    total_amount: float
    start_date: date
    end_date: Optional[date] = None
    recognition_method: str
    journal_entry_template: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccrualEntryResponse(BaseModel):
    id: uuid.UUID
    schedule_id: uuid.UUID
    period_date: date
    recognized_amount: float
    journal_entry_id: Optional[uuid.UUID] = None
    status: str
    posted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccrualScheduleDetailResponse(AccrualScheduleResponse):
    entries: list[AccrualEntryResponse] = []


class GenerateEntriesRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    periods: int = 12
