import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.accounting import Client
from app.models.tax import TaxReturn, SignatureRequest, TaxOrganizer
from app.models.organization import User
from app.schemas.tax import (
    TaxReturnCreate,
    TaxReturnUpdate,
    TaxReturnResponse,
    SignatureRequestCreate,
    SignatureRequestResponse,
    TaxOrganizerCreate,
    TaxOrganizerUpdate,
    TaxOrganizerResponse,
)

router = APIRouter()


@router.get("/returns", response_model=list[TaxReturnResponse])
async def list_tax_returns(
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TaxReturn).join(Client, TaxReturn.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TaxReturn.client_id == client_id)
    if status_filter:
        query = query.where(TaxReturn.status == status_filter)
    query = query.order_by(TaxReturn.tax_year.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/returns", response_model=TaxReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_return(
    req: TaxReturnCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    tr = TaxReturn(
        client_id=req.client_id,
        tax_year=req.tax_year,
        form_type=req.form_type,
        status=req.status,
        assigned_to=req.assigned_to,
        due_date=req.due_date,
    )
    db.add(tr)
    await db.commit()
    await db.refresh(tr)
    return tr


@router.put("/returns/{return_id}", response_model=TaxReturnResponse)
async def update_tax_return(
    return_id: uuid.UUID,
    req: TaxReturnUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tr = await db.get(TaxReturn, return_id)
    if not tr:
        raise HTTPException(status_code=404, detail="Tax return not found")
    client = await db.get(Client, tr.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Tax return not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(tr, field, value)
    await db.commit()
    await db.refresh(tr)
    return tr


@router.get("/organizers", response_model=list[TaxOrganizerResponse])
async def list_organizers(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TaxOrganizer).join(Client, TaxOrganizer.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(TaxOrganizer.client_id == client_id)
    query = query.order_by(TaxOrganizer.tax_year.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/organizers", response_model=TaxOrganizerResponse, status_code=status.HTTP_201_CREATED)
async def create_organizer(
    req: TaxOrganizerCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    organizer = TaxOrganizer(
        client_id=req.client_id,
        tax_year=req.tax_year,
        form_json=req.form_json,
        status=req.status,
    )
    db.add(organizer)
    await db.commit()
    await db.refresh(organizer)
    return organizer


@router.put("/organizers/{organizer_id}", response_model=TaxOrganizerResponse)
async def update_organizer(
    organizer_id: uuid.UUID,
    req: TaxOrganizerUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    organizer = await db.get(TaxOrganizer, organizer_id)
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")
    client = await db.get(Client, organizer.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Organizer not found")
    if req.status == "completed" and organizer.status != "completed":
        organizer.completed_at = datetime.now(timezone.utc)
    for field, value in req.model_dump(exclude_unset=True).items():
        if field == "completed_at":
            continue
        setattr(organizer, field, value)
    await db.commit()
    await db.refresh(organizer)
    return organizer


@router.post("/signatures", response_model=SignatureRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_signature_request(
    req: SignatureRequestCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    tr = await db.get(TaxReturn, req.tax_return_id)
    if not tr:
        raise HTTPException(status_code=404, detail="Tax return not found")
    client = await db.get(Client, tr.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Tax return not found")

    sig = SignatureRequest(
        tax_return_id=req.tax_return_id,
        signer_email=req.signer_email,
        signer_name=req.signer_name,
        document_url=req.document_url,
        auth_method=req.auth_method,
    )
    db.add(sig)
    await db.commit()
    await db.refresh(sig)
    return sig


@router.put("/signatures/{sig_id}", response_model=SignatureRequestResponse)
async def update_signature(
    sig_id: uuid.UUID,
    status_req: str,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    sig = await db.get(SignatureRequest, sig_id)
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    tr = await db.get(TaxReturn, sig.tax_return_id)
    client = await db.get(Client, tr.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Signature request not found")

    sig.status = status_req
    if status_req == "signed":
        sig.signed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(sig)
    return sig
