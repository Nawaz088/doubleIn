import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClientCreate(BaseModel):
    name: str
    entity_type: str = "llc"
    status: str = "active"
    properties: Optional[dict] = None
    close_day: Optional[int] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    entity_type: Optional[str] = None
    status: Optional[str] = None
    properties: Optional[dict] = None
    close_day: Optional[int] = None


class ClientResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    entity_type: str
    status: str
    properties: Optional[dict] = None
    close_day: Optional[int] = None
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientDetailResponse(ClientResponse):
    task_lists: list = []
    open_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0


class ClientDashboardResponse(BaseModel):
    total_tasks: int = 0
    completed_tasks: int = 0
    open_tasks: int = 0
    in_progress_tasks: int = 0
    in_review_tasks: int = 0
    completion_rate: float = 0.0
    bank_transaction_count: int = 0
    journal_entry_count: int = 0
    recent_activity: list = []
    upcoming_deadlines: list = []
