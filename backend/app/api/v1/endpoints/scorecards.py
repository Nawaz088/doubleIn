import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.scorecard import (
    ScorecardTemplate,
    Scorecard,
    KpiDefinition,
    ScorecardKpiEntry,
    ScorecardAttendee,
    ScorecardActionItem,
    ScorecardComment,
)
from app.models.organization import User
from app.schemas.scorecard import (
    ScorecardTemplateCreate,
    ScorecardTemplateUpdate,
    ScorecardTemplateResponse,
    ScorecardCreate,
    ScorecardUpdate,
    ScorecardResponse,
    ScorecardDetailResponse,
    KpiDefinitionCreate,
    KpiDefinitionUpdate,
    KpiDefinitionResponse,
    KpiEntryUpdate,
    KpiEntryResponse,
    AttendeeCreate,
    AttendeeResponse,
    ActionItemCreate,
    ActionItemUpdate,
    ActionItemResponse,
    CommentCreate,
    CommentResponse,
    ScorecardDashboardResponse,
)
from app.services.scorecard_engine import compute_all_auto_kpis

router = APIRouter()

PREDEFINED_KPI_NAMES = {
    "tasks-completed": "Tasks Completed",
    "closes-on-time-pct": "Closes On Time %",
    "avg-close-time": "Avg Close Time",
    "reports-generated": "Reports Generated",
    "utilization-rate": "Utilization Rate",
    "net-client-growth": "Net Client Growth",
    "portal-adoption-rate": "Portal Adoption Rate",
    "open-action-items": "Open Action Items",
}


# ---------------------------------------------------------------------------
# KPI Definitions
# ---------------------------------------------------------------------------

@router.get("/definitions", response_model=list[KpiDefinitionResponse])
async def list_kpi_definitions(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(KpiDefinition)
        .where(KpiDefinition.org_id == user.org_id)
        .order_by(KpiDefinition.category, KpiDefinition.sort_order)
    )
    return result.scalars().all()


@router.post("/definitions", response_model=KpiDefinitionResponse, status_code=201)
async def create_kpi_definition(
    req: KpiDefinitionCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    kpi = KpiDefinition(
        org_id=user.org_id,
        name=req.name,
        description=req.description,
        category=req.category,
        unit=req.unit,
        data_source=req.data_source,
        computation_config=req.computation_config,
        sort_order=req.sort_order,
    )
    db.add(kpi)
    await db.commit()
    await db.refresh(kpi)
    return kpi


@router.put("/definitions/{def_id}", response_model=KpiDefinitionResponse)
async def update_kpi_definition(
    def_id: uuid.UUID,
    req: KpiDefinitionUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    kpi = await db.get(KpiDefinition, def_id)
    if not kpi or kpi.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="KPI definition not found")
    if kpi.is_prebuilt:
        raise HTTPException(status_code=400, detail="Cannot modify prebuilt KPI definitions")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(kpi, field, value)
    await db.commit()
    await db.refresh(kpi)
    return kpi


@router.delete("/definitions/{def_id}", status_code=204)
async def delete_kpi_definition(
    def_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    kpi = await db.get(KpiDefinition, def_id)
    if not kpi or kpi.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="KPI definition not found")
    if kpi.is_prebuilt:
        raise HTTPException(status_code=400, detail="Cannot delete prebuilt KPI definitions")
    kpi.is_active = False
    await db.commit()


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

@router.get("/templates", response_model=list[ScorecardTemplateResponse])
async def list_templates(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(ScorecardTemplate)
        .where(ScorecardTemplate.org_id == user.org_id, ScorecardTemplate.is_active == True)
        .order_by(ScorecardTemplate.created_at.desc())
    )
    return result.scalars().all()


@router.post("/templates", response_model=ScorecardTemplateResponse, status_code=201)
async def create_template(
    req: ScorecardTemplateCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tmpl = ScorecardTemplate(
        org_id=user.org_id,
        name=req.name,
        description=req.description,
        frequency=req.frequency,
        kpi_definition_ids=req.kpi_definition_ids,
    )
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)
    return tmpl


@router.put("/templates/{template_id}", response_model=ScorecardTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    req: ScorecardTemplateUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tmpl = await db.get(ScorecardTemplate, template_id)
    if not tmpl or tmpl.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Template not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(tmpl, field, value)
    await db.commit()
    await db.refresh(tmpl)
    return tmpl


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tmpl = await db.get(ScorecardTemplate, template_id)
    if not tmpl or tmpl.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Template not found")
    tmpl.is_active = False
    await db.commit()


# ---------------------------------------------------------------------------
# Scorecards
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[ScorecardResponse])
async def list_scorecards(
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(Scorecard).where(Scorecard.org_id == user.org_id)
    if status_filter:
        query = query.where(Scorecard.status == status_filter)
    query = query.order_by(Scorecard.period_start.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ScorecardDetailResponse, status_code=201)
async def create_scorecard(
    req: ScorecardCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)

    kpi_ids = None
    if req.template_id:
        tmpl = await db.get(ScorecardTemplate, req.template_id)
        if not tmpl or tmpl.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Template not found")
        kpi_ids = tmpl.kpi_definition_ids

    sc = Scorecard(
        org_id=user.org_id,
        template_id=req.template_id,
        name=req.name,
        period_start=req.period_start,
        period_end=req.period_end,
        created_by=user_id,
        meeting_date=req.meeting_date,
        meeting_notes=req.meeting_notes,
    )
    db.add(sc)
    await db.flush()

    auto_values = await compute_all_auto_kpis(user.org_id, req.period_start, req.period_end)

    if kpi_ids:
        for idx, kpi_id_str in enumerate(kpi_ids):
            kpi = await db.get(KpiDefinition, uuid.UUID(kpi_id_str))
            if kpi and kpi.org_id == user.org_id:
                db.add(ScorecardKpiEntry(
                    scorecard_id=sc.id,
                    kpi_definition_id=kpi.id,
                    sort_order=idx,
                ))
    else:
        result = await db.execute(
            select(KpiDefinition)
            .where(KpiDefinition.org_id == user.org_id, KpiDefinition.is_active == True)
            .order_by(KpiDefinition.category, KpiDefinition.sort_order)
        )
        kpis = result.scalars().all()
        for kpi in kpis:
            entry = ScorecardKpiEntry(
                scorecard_id=sc.id,
                kpi_definition_id=kpi.id,
                sort_order=kpi.sort_order,
            )
            db.add(entry)

    await db.flush()

    entry_result = await db.execute(
        select(ScorecardKpiEntry, KpiDefinition)
        .join(KpiDefinition, KpiDefinition.id == ScorecardKpiEntry.kpi_definition_id)
        .where(ScorecardKpiEntry.scorecard_id == sc.id)
    )
    for entry, kpi_def in entry_result:
        mapped_name = None
        for key, name in PREDEFINED_KPI_NAMES.items():
            if kpi_def.name.lower() == name.lower():
                mapped_name = key
                break

        if mapped_name and mapped_name in auto_values and auto_values[mapped_name] is not None:
            entry.actual_value = float(auto_values[mapped_name])
        elif kpi_def.data_source == "auto" and kpi_def.computation_config:
            pass

    await db.commit()
    await db.refresh(sc)
    return await _build_scorecard_detail(sc.id, db)


@router.get("/{scorecard_id}", response_model=ScorecardDetailResponse)
async def get_scorecard(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    return await _build_scorecard_detail(sc.id, db)


@router.put("/{scorecard_id}", response_model=ScorecardDetailResponse)
async def update_scorecard(
    scorecard_id: uuid.UUID,
    req: ScorecardUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(sc, field, value)
    await db.commit()
    await db.refresh(sc)
    return await _build_scorecard_detail(sc.id, db)


@router.delete("/{scorecard_id}", status_code=204)
async def delete_scorecard(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    sc.status = "archived"
    await db.commit()


@router.post("/{scorecard_id}/publish", response_model=ScorecardDetailResponse)
async def publish_scorecard(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    sc.status = "published"
    sc.published_at = func.now()
    await db.commit()
    await db.refresh(sc)
    return await _build_scorecard_detail(sc.id, db)


@router.post("/{scorecard_id}/refresh", response_model=ScorecardDetailResponse)
async def refresh_scorecard(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    auto_values = await compute_all_auto_kpis(user.org_id, sc.period_start, sc.period_end)

    entry_result = await db.execute(
        select(ScorecardKpiEntry, KpiDefinition)
        .join(KpiDefinition, KpiDefinition.id == ScorecardKpiEntry.kpi_definition_id)
        .where(ScorecardKpiEntry.scorecard_id == sc.id)
    )
    for entry, kpi_def in entry_result:
        mapped_name = None
        for key, name in PREDEFINED_KPI_NAMES.items():
            if kpi_def.name.lower() == name.lower():
                mapped_name = key
                break

        if mapped_name and mapped_name in auto_values and auto_values[mapped_name] is not None:
            entry.actual_value = float(auto_values[mapped_name])

    await db.commit()
    await db.refresh(sc)
    return await _build_scorecard_detail(sc.id, db)


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

@router.put("/{scorecard_id}/entries/{entry_id}", response_model=KpiEntryResponse)
async def update_kpi_entry(
    scorecard_id: uuid.UUID,
    entry_id: uuid.UUID,
    req: KpiEntryUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    entry = await db.get(ScorecardKpiEntry, entry_id)
    if not entry or entry.scorecard_id != scorecard_id:
        raise HTTPException(status_code=404, detail="KPI entry not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)

    kpi_def = await db.get(KpiDefinition, entry.kpi_definition_id)
    return KpiEntryResponse(
        id=entry.id,
        scorecard_id=entry.scorecard_id,
        kpi_definition_id=entry.kpi_definition_id,
        kpi_name=kpi_def.name if kpi_def else "Unknown",
        kpi_category=kpi_def.category if kpi_def else "custom",
        kpi_unit=kpi_def.unit if kpi_def else None,
        target_value=entry.target_value,
        actual_value=entry.actual_value,
        previous_value=entry.previous_value,
        status=entry.status,
        notes=entry.notes,
        sort_order=entry.sort_order,
        created_at=entry.created_at,
    )


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------

@router.post("/{scorecard_id}/attendees", response_model=AttendeeResponse, status_code=201)
async def add_attendee(
    scorecard_id: uuid.UUID,
    req: AttendeeCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    att = ScorecardAttendee(scorecard_id=sc.id, user_id=req.user_id, role=req.role)
    db.add(att)
    await db.commit()
    await db.refresh(att)
    return att


@router.delete("/{scorecard_id}/attendees/{attendee_id}", status_code=204)
async def remove_attendee(
    scorecard_id: uuid.UUID,
    attendee_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    att = await db.get(ScorecardAttendee, attendee_id)
    if not att or att.scorecard_id != scorecard_id:
        raise HTTPException(status_code=404, detail="Attendee not found")
    await db.delete(att)
    await db.commit()


# ---------------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------------

@router.post("/{scorecard_id}/action-items", response_model=ActionItemResponse, status_code=201)
async def create_action_item(
    scorecard_id: uuid.UUID,
    req: ActionItemCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    item = ScorecardActionItem(
        scorecard_id=sc.id,
        kpi_entry_id=req.kpi_entry_id,
        assigned_to=req.assigned_to,
        title=req.title,
        description=req.description,
        due_date=req.due_date,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{scorecard_id}/action-items/{item_id}", response_model=ActionItemResponse)
async def update_action_item(
    scorecard_id: uuid.UUID,
    item_id: uuid.UUID,
    req: ActionItemUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    item = await db.get(ScorecardActionItem, item_id)
    if not item or item.scorecard_id != scorecard_id:
        raise HTTPException(status_code=404, detail="Action item not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{scorecard_id}/action-items/{item_id}", status_code=204)
async def delete_action_item(
    scorecard_id: uuid.UUID,
    item_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    item = await db.get(ScorecardActionItem, item_id)
    if not item or item.scorecard_id != scorecard_id:
        raise HTTPException(status_code=404, detail="Action item not found")
    await db.delete(item)
    await db.commit()


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

@router.post("/{scorecard_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    scorecard_id: uuid.UUID,
    req: CommentCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    comment = ScorecardComment(
        scorecard_id=sc.id,
        kpi_entry_id=req.kpi_entry_id,
        user_id=user_id,
        content=req.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/{scorecard_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    result = await db.execute(
        select(ScorecardComment)
        .where(ScorecardComment.scorecard_id == sc.id)
        .order_by(ScorecardComment.created_at)
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard", response_model=ScorecardDashboardResponse)
async def get_dashboard(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(Scorecard)
        .where(
            Scorecard.org_id == user.org_id,
            Scorecard.status.in_(["draft", "in_review", "published"]),
        )
        .order_by(Scorecard.period_start.desc())
        .limit(1)
    )
    sc = result.scalar_one_or_none()
    if not sc:
        return ScorecardDashboardResponse()

    detail = await _build_scorecard_detail(sc.id, db)

    history_result = await db.execute(
        select(ScorecardKpiEntry.actual_value, Scorecard.period_start, KpiDefinition.name)
        .join(Scorecard, Scorecard.id == ScorecardKpiEntry.scorecard_id)
        .join(KpiDefinition, KpiDefinition.id == ScorecardKpiEntry.kpi_definition_id)
        .where(Scorecard.org_id == user.org_id, KpiDefinition.is_active == True)
        .order_by(Scorecard.period_start.desc())
        .limit(100)
    )
    historical = [{"kpi": row[2], "value": float(row[0]) if row[0] else None, "period": str(row[1])} for row in history_result]

    return ScorecardDashboardResponse(scorecard=detail, historical_kpis=historical)


@router.get("/history/{kpi_id}")
async def get_kpi_history(
    kpi_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    result = await db.execute(
        select(ScorecardKpiEntry.actual_value, Scorecard.period_start)
        .join(Scorecard, Scorecard.id == ScorecardKpiEntry.scorecard_id)
        .where(
            ScorecardKpiEntry.kpi_definition_id == kpi_id,
            Scorecard.org_id == user.org_id,
        )
        .order_by(Scorecard.period_start)
    )
    return [
        {"period": str(row[1]), "value": float(row[0]) if row[0] else None}
        for row in result
    ]


# ---------------------------------------------------------------------------
# Export (placeholder)
# ---------------------------------------------------------------------------

@router.get("/{scorecard_id}/export/pdf")
async def export_pdf(
    scorecard_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sc = await db.get(Scorecard, scorecard_id)
    if not sc or sc.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    return {"message": "PDF export not yet implemented", "scorecard_id": str(sc.id)}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _build_scorecard_detail(sc_id: uuid.UUID, db: AsyncSession) -> ScorecardDetailResponse:
    sc = await db.get(Scorecard, sc_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Scorecard not found")

    entry_result = await db.execute(
        select(ScorecardKpiEntry, KpiDefinition)
        .join(KpiDefinition, KpiDefinition.id == ScorecardKpiEntry.kpi_definition_id, isouter=True)
        .where(ScorecardKpiEntry.scorecard_id == sc.id)
        .order_by(ScorecardKpiEntry.sort_order)
    )

    entries = []
    for entry, kpi_def in entry_result:
        entries.append(KpiEntryResponse(
            id=entry.id,
            scorecard_id=entry.scorecard_id,
            kpi_definition_id=entry.kpi_definition_id,
            kpi_name=kpi_def.name if kpi_def else "Unknown",
            kpi_category=kpi_def.category if kpi_def else "custom",
            kpi_unit=kpi_def.unit if kpi_def else None,
            target_value=entry.target_value,
            actual_value=entry.actual_value,
            previous_value=entry.previous_value,
            status=entry.status,
            notes=entry.notes,
            sort_order=entry.sort_order,
            created_at=entry.created_at,
        ))

    att_result = await db.execute(
        select(ScorecardAttendee).where(ScorecardAttendee.scorecard_id == sc.id)
    )
    attendees = [
        AttendeeResponse(
            id=a.id, user_id=a.user_id, role=a.role, created_at=a.created_at
        ) for a in att_result.scalars()
    ]

    ai_result = await db.execute(
        select(ScorecardActionItem)
        .where(ScorecardActionItem.scorecard_id == sc.id)
        .order_by(ScorecardActionItem.created_at)
    )
    action_items = [
        ActionItemResponse(
            id=ai.id,
            kpi_entry_id=ai.kpi_entry_id,
            assigned_to=ai.assigned_to,
            title=ai.title,
            description=ai.description,
            due_date=ai.due_date,
            status=ai.status,
            created_at=ai.created_at,
        ) for ai in ai_result.scalars()
    ]

    comment_result = await db.execute(
        select(ScorecardComment)
        .where(ScorecardComment.scorecard_id == sc.id)
        .order_by(ScorecardComment.created_at)
    )
    comments = [
        CommentResponse(
            id=c.id,
            scorecard_id=c.scorecard_id,
            kpi_entry_id=c.kpi_entry_id,
            user_id=c.user_id,
            content=c.content,
            created_at=c.created_at,
        ) for c in comment_result.scalars()
    ]

    return ScorecardDetailResponse(
        id=sc.id,
        name=sc.name,
        period_start=sc.period_start,
        period_end=sc.period_end,
        status=sc.status,
        template_id=sc.template_id,
        created_by=sc.created_by,
        meeting_date=sc.meeting_date,
        meeting_notes=sc.meeting_notes,
        published_at=sc.published_at,
        created_at=sc.created_at,
        updated_at=sc.updated_at,
        kpi_entries=entries,
        attendees=attendees,
        action_items=action_items,
        comments=comments,
    )
