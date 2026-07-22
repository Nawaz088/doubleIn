import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Client(BaseModel):
    __tablename__ = "clients"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), default="llc")
    status: Mapped[str] = mapped_column(String(20), default="active")
    properties: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    close_day: Mapped[int | None] = mapped_column(Integer, nullable=True)

    task_lists: Mapped[list["TaskList"]] = relationship(back_populates="client")


class TaskList(BaseModel):
    __tablename__ = "task_lists"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_template: Mapped[bool] = mapped_column(default=False)

    client: Mapped[Client] = relationship(back_populates="task_lists")
    tasks: Mapped[list["Task"]] = relationship(back_populates="task_list", order_by="Task.sort_order")


class Task(BaseModel):
    __tablename__ = "tasks"

    task_list_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("task_lists.id"), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="todo")
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(default=False)
    recurring_schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    task_list: Mapped[TaskList] = relationship(back_populates="tasks")
    parent: Mapped["Task | None"] = relationship("Task", remote_side="Task.id", back_populates="children")
    children: Mapped[list["Task"]] = relationship("Task", back_populates="parent")


class PortalActivity(BaseModel):
    __tablename__ = "portal_activities"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    activity_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
