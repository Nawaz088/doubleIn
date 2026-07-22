import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PortalMessageCreate(BaseModel):
    client_id: uuid.UUID
    sender_type: str = "firm"
    content: str
    message_type: str = "general"
    related_transaction_id: Optional[str] = None
    attachment_url: Optional[str] = None


class PortalMessageResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    org_id: uuid.UUID
    sender_type: str
    sender_id: uuid.UUID
    content: str
    message_type: str
    related_transaction_id: Optional[str] = None
    attachment_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PortalDocumentResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    org_id: uuid.UUID
    uploaded_by: str
    user_id: uuid.UUID
    file_url: str
    file_name: str
    doc_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortalDocumentUpload(BaseModel):
    client_id: uuid.UUID
    uploaded_by: str = "firm"
    file_url: str
    file_name: str
    doc_type: str = "other"


class BrandingUpdate(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    domain: Optional[str] = None
    firm_name: Optional[str] = None


class BrandingResponse(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    domain: Optional[str] = None
    firm_name: Optional[str] = None
