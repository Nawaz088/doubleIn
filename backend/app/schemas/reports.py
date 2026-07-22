import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReportPackageCreate(BaseModel):
    client_id: uuid.UUID
    name: str
    period_start: date
    period_end: date
    sections_json: Optional[dict] = None


class ReportPackageUpdate(BaseModel):
    name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    sections_json: Optional[dict] = None


class ReportSectionCreate(BaseModel):
    section_type: str
    config: Optional[dict] = None
    data: Optional[dict] = None
    sort_order: int = 0


class ReportSectionUpdate(BaseModel):
    section_type: Optional[str] = None
    config: Optional[dict] = None
    data: Optional[dict] = None
    sort_order: Optional[int] = None


class ReportSectionResponse(BaseModel):
    id: uuid.UUID
    report_package_id: uuid.UUID
    section_type: str
    config: Optional[dict] = None
    data: Optional[dict] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportPackageResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    org_id: uuid.UUID
    name: str
    period_start: date
    period_end: date
    status: str
    sections_json: Optional[dict] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportPackageDetailResponse(ReportPackageResponse):
    sections: list[ReportSectionResponse] = []


class ReviewReportCreate(BaseModel):
    client_id: uuid.UUID
    name: str
    report_type: str
    filters: Optional[dict] = None
    is_active: bool = True


class ReviewReportResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    org_id: uuid.UUID
    name: str
    report_type: str
    filters: Optional[dict] = None
    is_active: bool
    findings: list["ReviewFindingResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewFindingResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    transaction_external_id: str
    transaction_date: date
    transaction_amount: float
    transaction_description: str
    issue: str
    suggested_action: Optional[str] = None
    status: str
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewFindingUpdate(BaseModel):
    status: Optional[str] = None
    resolved_by: Optional[uuid.UUID] = None
