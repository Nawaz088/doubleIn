import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmailMessageResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    client_id: Optional[uuid.UUID] = None
    from_address: str
    to_address: list
    subject: str
    body_text: str
    external_id: str
    thread_id: str
    received_at: datetime
    is_read: bool
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailMessageDetailResponse(EmailMessageResponse):
    body_html: Optional[str] = None
