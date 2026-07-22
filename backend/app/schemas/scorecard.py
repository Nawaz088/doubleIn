import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class KpiDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "custom"
    unit: Optional[str] = None
    data_source: str = "manual"
    computation_config: Optional[dict] = None
    sort_order: int = 0


class KpiDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    data_source: Optional[str] = None
    computation_config: Optional[dict] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class KpiDefinitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    category: str
    unit: Optional[str] = None
    data_source: str
    computation_config: Optional[dict] = None
    is_prebuilt: bool
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScorecardTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str = "monthly"
    kpi_definition_ids: Optional[list[str]] = None


class ScorecardTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    kpi_definition_ids: Optional[list[str]] = None
    is_active: Optional[bool] = None


class ScorecardTemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    frequency: str
    is_active: bool
    kpi_definition_ids: Optional[list] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScorecardCreate(BaseModel):
    name: str
    period_start: date
    period_end: date
    template_id: Optional[uuid.UUID] = None
    meeting_date: Optional[datetime] = None
    meeting_notes: Optional[str] = None


class ScorecardUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    meeting_date: Optional[datetime] = None
    meeting_notes: Optional[str] = None


class ScorecardResponse(BaseModel):
    id: uuid.UUID
    name: str
    period_start: date
    period_end: date
    status: str
    template_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    meeting_date: Optional[datetime] = None
    meeting_notes: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KpiEntryUpdate(BaseModel):
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class KpiEntryResponse(BaseModel):
    id: uuid.UUID
    scorecard_id: uuid.UUID
    kpi_definition_id: uuid.UUID
    kpi_name: str
    kpi_category: str
    kpi_unit: Optional[str] = None
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScorecardDetailResponse(ScorecardResponse):
    kpi_entries: list[KpiEntryResponse] = []
    attendees: list["AttendeeResponse"] = []
    action_items: list["ActionItemResponse"] = []
    comments: list["CommentResponse"] = []


class AttendeeCreate(BaseModel):
    user_id: uuid.UUID
    role: str = "attendee"


class AttendeeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ActionItemCreate(BaseModel):
    kpi_entry_id: Optional[uuid.UUID] = None
    assigned_to: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None


class ActionItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    status: Optional[str] = None


class ActionItemResponse(BaseModel):
    id: uuid.UUID
    kpi_entry_id: Optional[uuid.UUID] = None
    assigned_to: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    kpi_entry_id: Optional[uuid.UUID] = None
    content: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    scorecard_id: uuid.UUID
    kpi_entry_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ScorecardDashboardResponse(BaseModel):
    scorecard: Optional[ScorecardDetailResponse] = None
    historical_kpis: list[dict] = []
