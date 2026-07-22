import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TaxReturnCreate(BaseModel):
    client_id: uuid.UUID
    tax_year: int
    form_type: str
    status: str = "draft"
    assigned_to: Optional[uuid.UUID] = None
    due_date: date


class TaxReturnUpdate(BaseModel):
    form_type: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    filed_date: Optional[date] = None


class TaxReturnResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    tax_year: int
    form_type: str
    status: str
    assigned_to: Optional[uuid.UUID] = None
    due_date: date
    filed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SignatureRequestCreate(BaseModel):
    tax_return_id: uuid.UUID
    signer_email: str
    signer_name: str
    document_url: str
    auth_method: str = "email"


class SignatureRequestResponse(BaseModel):
    id: uuid.UUID
    tax_return_id: uuid.UUID
    signer_email: str
    signer_name: str
    document_url: str
    auth_method: str
    status: str
    signed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaxOrganizerCreate(BaseModel):
    client_id: uuid.UUID
    tax_year: int
    form_json: Optional[dict] = None
    status: str = "draft"


class TaxOrganizerUpdate(BaseModel):
    form_json: Optional[dict] = None
    status: Optional[str] = None


class TaxOrganizerResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    tax_year: int
    form_json: Optional[dict] = None
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
