import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.reports import ReportPackage, ReportSection
from app.models.organization import User, Organization
from app.schemas.reports import (
    ReportPackageCreate,
    ReportPackageUpdate,
    ReportPackageResponse,
    ReportPackageDetailResponse,
    ReportSectionCreate,
    ReportSectionUpdate,
    ReportSectionResponse,
)

router = APIRouter()


@router.get("/", response_model=list[ReportPackageResponse])
async def list_report_packages(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(ReportPackage).where(ReportPackage.org_id == user.org_id)
    if client_id:
        query = query.where(ReportPackage.client_id == client_id)
    query = query.order_by(ReportPackage.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ReportPackageDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_report_package(
    req: ReportPackageCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    pkg = ReportPackage(
        client_id=req.client_id,
        org_id=user.org_id,
        name=req.name,
        period_start=req.period_start,
        period_end=req.period_end,
        sections_json=req.sections_json,
    )
    db.add(pkg)
    await db.commit()
    await db.refresh(pkg)
    return ReportPackageDetailResponse(
        id=pkg.id, client_id=pkg.client_id, org_id=pkg.org_id,
        name=pkg.name, period_start=pkg.period_start, period_end=pkg.period_end,
        status=pkg.status, sections_json=pkg.sections_json, published_at=pkg.published_at,
        created_at=pkg.created_at, updated_at=pkg.updated_at, sections=[],
    )


@router.get("/{package_id}", response_model=ReportPackageDetailResponse)
async def get_report_package(
    package_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")

    sections_result = await db.execute(
        select(ReportSection).where(ReportSection.report_package_id == pkg.id).order_by(ReportSection.sort_order)
    )
    sections = [
        ReportSectionResponse(
            id=s.id, report_package_id=s.report_package_id, section_type=s.section_type,
            config=s.config, data=s.data, sort_order=s.sort_order,
            created_at=s.created_at, updated_at=s.updated_at,
        ) for s in sections_result.scalars().all()
    ]
    return ReportPackageDetailResponse(
        id=pkg.id, client_id=pkg.client_id, org_id=pkg.org_id,
        name=pkg.name, period_start=pkg.period_start, period_end=pkg.period_end,
        status=pkg.status, sections_json=pkg.sections_json, published_at=pkg.published_at,
        created_at=pkg.created_at, updated_at=pkg.updated_at, sections=sections,
    )


@router.put("/{package_id}", response_model=ReportPackageDetailResponse)
async def update_report_package(
    package_id: uuid.UUID,
    req: ReportPackageUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(pkg, field, value)
    await db.commit()
    await db.refresh(pkg)

    sections_result = await db.execute(
        select(ReportSection).where(ReportSection.report_package_id == pkg.id).order_by(ReportSection.sort_order)
    )
    sections = [
        ReportSectionResponse(
            id=s.id, report_package_id=s.report_package_id, section_type=s.section_type,
            config=s.config, data=s.data, sort_order=s.sort_order,
            created_at=s.created_at, updated_at=s.updated_at,
        ) for s in sections_result.scalars().all()
    ]
    return ReportPackageDetailResponse(
        id=pkg.id, client_id=pkg.client_id, org_id=pkg.org_id,
        name=pkg.name, period_start=pkg.period_start, period_end=pkg.period_end,
        status=pkg.status, sections_json=pkg.sections_json, published_at=pkg.published_at,
        created_at=pkg.created_at, updated_at=pkg.updated_at, sections=sections,
    )


@router.post("/{package_id}/publish", response_model=ReportPackageDetailResponse)
async def publish_report_package(
    package_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")
    pkg.status = "published"
    pkg.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(pkg)

    sections_result = await db.execute(
        select(ReportSection).where(ReportSection.report_package_id == pkg.id).order_by(ReportSection.sort_order)
    )
    sections = [
        ReportSectionResponse(
            id=s.id, report_package_id=s.report_package_id, section_type=s.section_type,
            config=s.config, data=s.data, sort_order=s.sort_order,
            created_at=s.created_at, updated_at=s.updated_at,
        ) for s in sections_result.scalars().all()
    ]
    return ReportPackageDetailResponse(
        id=pkg.id, client_id=pkg.client_id, org_id=pkg.org_id,
        name=pkg.name, period_start=pkg.period_start, period_end=pkg.period_end,
        status=pkg.status, sections_json=pkg.sections_json, published_at=pkg.published_at,
        created_at=pkg.created_at, updated_at=pkg.updated_at, sections=sections,
    )


@router.get("/{package_id}/export")
async def export_report_package(
    package_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.pdf_export import generate_report_pdf

    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")

    org = await db.get(Organization, user.org_id)
    client = await db.get(Client, pkg.client_id)
    sections_result = await db.execute(
        select(ReportSection)
        .where(ReportSection.report_package_id == package_id)
        .order_by(ReportSection.sort_order)
    )
    sections = sections_result.scalars().all()

    sections_data = [
        {"section_type": s.section_type, "data": s.data, "sort_order": s.sort_order}
        for s in sections
    ]

    pdf_bytes = generate_report_pdf(
        report_name=pkg.name,
        period=f"{pkg.period_start} to {pkg.period_end}",
        sections=sections_data,
        org_name=org.name if org else "DoubleHQ",
        client_name=client.name if client else "",
    )

    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{pkg.name}.pdf"'},
    )


@router.post("/{package_id}/sections", response_model=ReportSectionResponse, status_code=201)
async def add_section(
    package_id: uuid.UUID,
    req: ReportSectionCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")

    section = ReportSection(
        report_package_id=package_id,
        section_type=req.section_type,
        config=req.config,
        data=req.data,
        sort_order=req.sort_order,
    )
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


@router.put("/{package_id}/sections/{section_id}", response_model=ReportSectionResponse)
async def update_section(
    package_id: uuid.UUID,
    section_id: uuid.UUID,
    req: ReportSectionUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")
    section = await db.get(ReportSection, section_id)
    if not section or section.report_package_id != package_id:
        raise HTTPException(status_code=404, detail="Section not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    await db.commit()
    await db.refresh(section)
    return section


@router.delete("/{package_id}/sections/{section_id}", status_code=204)
async def delete_section(
    package_id: uuid.UUID,
    section_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    pkg = await db.get(ReportPackage, package_id)
    if not pkg or pkg.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Report package not found")
    section = await db.get(ReportSection, section_id)
    if not section or section.report_package_id != package_id:
        raise HTTPException(status_code=404, detail="Section not found")
    await db.delete(section)
    await db.commit()
