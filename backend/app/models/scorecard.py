import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ScorecardTemplate(BaseModel):
    __tablename__ = "scorecard_templates"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str] = mapped_column(String(20), default="monthly")  # weekly, monthly, quarterly, yearly
    is_active: Mapped[bool] = mapped_column(default=True)
    kpi_definition_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    scorecards: Mapped[list["Scorecard"]] = relationship(back_populates="template")


class Scorecard(BaseModel):
    __tablename__ = "scorecards"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scorecard_templates.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, in_review, published, archived
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    meeting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meeting_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped[ScorecardTemplate | None] = relationship(back_populates="scorecards")
    kpi_entries: Mapped[list["ScorecardKpiEntry"]] = relationship(back_populates="scorecard", cascade="all, delete-orphan")
    attendees: Mapped[list["ScorecardAttendee"]] = relationship(back_populates="scorecard", cascade="all, delete-orphan")
    action_items: Mapped[list["ScorecardActionItem"]] = relationship(back_populates="scorecard", cascade="all, delete-orphan")
    comments: Mapped[list["ScorecardComment"]] = relationship(back_populates="scorecard", cascade="all, delete-orphan")


class KpiDefinition(BaseModel):
    __tablename__ = "kpi_definitions"

    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="custom")  # productivity, financial, client_health, custom
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)  # count, %, $, hours, days, etc.
    data_source: Mapped[str] = mapped_column(String(20), default="manual")  # manual, auto
    computation_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_prebuilt: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    entries: Mapped[list["ScorecardKpiEntry"]] = relationship(back_populates="kpi_definition")


class ScorecardKpiEntry(BaseModel):
    __tablename__ = "scorecard_kpi_entries"

    scorecard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scorecards.id"), nullable=False, index=True)
    kpi_definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kpi_definitions.id"), nullable=False)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    previous_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # on_track, at_risk, behind, achieved
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    scorecard: Mapped["Scorecard"] = relationship(back_populates="kpi_entries")
    kpi_definition: Mapped["KpiDefinition"] = relationship(back_populates="entries")
    comments: Mapped[list["ScorecardComment"]] = relationship(back_populates="kpi_entry")
    action_items: Mapped[list["ScorecardActionItem"]] = relationship(back_populates="kpi_entry")


class ScorecardAttendee(BaseModel):
    __tablename__ = "scorecard_attendees"

    scorecard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scorecards.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="attendee")  # presenter, attendee, note_taker

    scorecard: Mapped["Scorecard"] = relationship(back_populates="attendees")


class ScorecardActionItem(BaseModel):
    __tablename__ = "scorecard_action_items"

    scorecard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scorecards.id"), nullable=False, index=True)
    kpi_entry_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scorecard_kpi_entries.id"), nullable=True)
    assigned_to: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, in_progress, completed

    scorecard: Mapped["Scorecard"] = relationship(back_populates="action_items")
    kpi_entry: Mapped[ScorecardKpiEntry | None] = relationship(back_populates="action_items")


class ScorecardComment(BaseModel):
    __tablename__ = "scorecard_comments"

    scorecard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scorecards.id"), nullable=False, index=True)
    kpi_entry_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scorecard_kpi_entries.id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    scorecard: Mapped["Scorecard"] = relationship(back_populates="comments")
    kpi_entry: Mapped[ScorecardKpiEntry | None] = relationship(back_populates="comments")
