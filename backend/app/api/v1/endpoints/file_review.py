import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.reports import ReviewReport, ReviewFinding
from app.models.organization import User
from app.schemas.reports import (
    ReviewReportCreate,
    ReviewReportResponse,
    ReviewFindingResponse,
    ReviewFindingUpdate,
)

router = APIRouter()


@router.get("/", response_model=list[ReviewReportResponse])
async def list_review_reports(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(ReviewReport).where(ReviewReport.org_id == user.org_id)
    if client_id:
        query = query.where(ReviewReport.client_id == client_id)
    query = query.order_by(ReviewReport.created_at.desc())
    result = await db.execute(query)
    reports = result.scalars().all()

    responses = []
    for r in reports:
        findings_result = await db.execute(
            select(ReviewFinding).where(ReviewFinding.report_id == r.id)
        )
        findings = [
            ReviewFindingResponse(
                id=f.id, report_id=f.report_id, transaction_external_id=f.transaction_external_id,
                transaction_date=f.transaction_date, transaction_amount=float(f.transaction_amount),
                transaction_description=f.transaction_description, issue=f.issue,
                suggested_action=f.suggested_action, status=f.status,
                resolved_by=f.resolved_by, resolved_at=f.resolved_at,
                created_at=f.created_at, updated_at=f.updated_at,
            ) for f in findings_result.scalars().all()
        ]
        responses.append(ReviewReportResponse(
            id=r.id, client_id=r.client_id, org_id=r.org_id,
            name=r.name, report_type=r.report_type, filters=r.filters,
            is_active=r.is_active, findings=findings,
            created_at=r.created_at, updated_at=r.updated_at,
        ))
    return responses


@router.post("/", response_model=ReviewReportResponse, status_code=status.HTTP_201_CREATED)
async def create_review_report(
    req: ReviewReportCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    report = ReviewReport(
        client_id=req.client_id,
        org_id=user.org_id,
        name=req.name,
        report_type=req.report_type,
        filters=req.filters,
        is_active=req.is_active,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return ReviewReportResponse(
        id=report.id, client_id=report.client_id, org_id=report.org_id,
        name=report.name, report_type=report.report_type, filters=report.filters,
        is_active=report.is_active, findings=[],
        created_at=report.created_at, updated_at=report.updated_at,
    )


@router.get("/{report_id}", response_model=ReviewReportResponse)
async def get_review_report(
    report_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    report = await db.get(ReviewReport, report_id)
    if not report or report.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Review report not found")

    findings_result = await db.execute(
        select(ReviewFinding).where(ReviewFinding.report_id == report.id)
    )
    findings = [
        ReviewFindingResponse(
            id=f.id, report_id=f.report_id, transaction_external_id=f.transaction_external_id,
            transaction_date=f.transaction_date, transaction_amount=float(f.transaction_amount),
            transaction_description=f.transaction_description, issue=f.issue,
            suggested_action=f.suggested_action, status=f.status,
            resolved_by=f.resolved_by, resolved_at=f.resolved_at,
            created_at=f.created_at, updated_at=f.updated_at,
        ) for f in findings_result.scalars().all()
    ]
    return ReviewReportResponse(
        id=report.id, client_id=report.client_id, org_id=report.org_id,
        name=report.name, report_type=report.report_type, filters=report.filters,
        is_active=report.is_active, findings=findings,
        created_at=report.created_at, updated_at=report.updated_at,
    )


@router.post("/{report_id}/findings/{finding_id}/resolve", response_model=ReviewFindingResponse)
async def resolve_finding(
    report_id: uuid.UUID,
    finding_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    report = await db.get(ReviewReport, report_id)
    if not report or report.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Review report not found")
    finding = await db.get(ReviewFinding, finding_id)
    if not finding or finding.report_id != report_id:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.status = "resolved"
    finding.resolved_by = user_id
    finding.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(finding)
    return ReviewFindingResponse(
        id=finding.id, report_id=finding.report_id, transaction_external_id=finding.transaction_external_id,
        transaction_date=finding.transaction_date, transaction_amount=float(finding.transaction_amount),
        transaction_description=finding.transaction_description, issue=finding.issue,
        suggested_action=finding.suggested_action, status=finding.status,
        resolved_by=finding.resolved_by, resolved_at=finding.resolved_at,
        created_at=finding.created_at, updated_at=finding.updated_at,
    )


@router.post("/{report_id}/refresh", response_model=ReviewReportResponse)
async def refresh_review_report(
    report_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    report = await db.get(ReviewReport, report_id)
    if not report or report.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Review report not found")

    findings_result = await db.execute(
        select(ReviewFinding).where(ReviewFinding.report_id == report.id)
    )
    findings = [
        ReviewFindingResponse(
            id=f.id, report_id=f.report_id, transaction_external_id=f.transaction_external_id,
            transaction_date=f.transaction_date, transaction_amount=float(f.transaction_amount),
            transaction_description=f.transaction_description, issue=f.issue,
            suggested_action=f.suggested_action, status=f.status,
            resolved_by=f.resolved_by, resolved_at=f.resolved_at,
            created_at=f.created_at, updated_at=f.updated_at,
        ) for f in findings_result.scalars().all()
    ]
    return ReviewReportResponse(
        id=report.id, client_id=report.client_id, org_id=report.org_id,
        name=report.name, report_type=report.report_type, filters=report.filters,
        is_active=report.is_active, findings=findings,
        created_at=report.created_at, updated_at=report.updated_at,
    )
