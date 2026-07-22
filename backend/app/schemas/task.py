import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskListCreate(BaseModel):
    client_id: uuid.UUID
    name: str
    sort_order: int = 0
    is_template: bool = False


class TaskListUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None
    is_template: Optional[bool] = None


class TaskListReorder(BaseModel):
    task_ids: list[uuid.UUID]


class TaskListResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    sort_order: int
    is_template: bool
    tasks: list["TaskResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    task_list_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    priority: str = "medium"
    status: str = "todo"
    tags: Optional[list[str]] = None
    is_recurring: bool = False
    recurring_schedule: Optional[dict] = None
    sort_order: int = 0


class TaskUpdate(BaseModel):
    task_list_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
    is_recurring: Optional[bool] = None
    recurring_schedule: Optional[dict] = None
    sort_order: Optional[int] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    task_list_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    priority: str
    status: str
    tags: Optional[list] = None
    is_recurring: bool
    recurring_schedule: Optional[dict] = None
    sort_order: int
    completed_at: Optional[datetime] = None
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskDetailResponse(TaskResponse):
    comments: list["TaskCommentResponse"] = []
    attachments: list["TaskAttachmentResponse"] = []
    children: list[TaskResponse] = []


class TaskCommentCreate(BaseModel):
    content: str
    attachment_url: Optional[str] = None


class TaskCommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    attachment_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskAttachmentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    file_url: str
    file_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
