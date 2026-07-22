import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.organization import User
from app.models.accounting import Client
from app.models.indian_tax import (
    GstRegistration, HsnSacCode, GstInvoice, GstInvoiceLine, GstReturn,
)
from app.schemas.indian_tax import (
    GstRegistrationCreate, GstRegistrationUpdate, GstRegistrationResponse,
    HsnSacCodeCreate, HsnSacCodeUpdate, HsnSacCodeResponse,
    GstInvoiceCreate, GstInvoiceUpdate, GstInvoiceResponse, GstInvoiceDetailResponse,
    GstReturnCreate, GstReturnUpdate, GstReturnResponse,
    GstComputeRequest, GstComputeResponse,
)
from app.services.gst_engine import validate_gstin, compute_invoice, get_due_date

router = APIRouter()


def _get_user_org(user_id: uuid.UUID, db: AsyncSession) -> User:
    user = db.get(User, user_id)
    return user


@router.get("/registrations", response_model=list[GstRegistrationResponse])
async def list_gst_registrations(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(GstRegistration).join(Client, GstRegistration.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(GstRegistration.client_id == client_id)
    query = query.order_by(GstRegistration.gstin)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/registrations", response_model=GstRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_registration(
    req: GstRegistrationCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    gstin = req.gstin.upper().strip()
    if not validate_gstin(gstin):
        raise HTTPException(status_code=400, detail="Invalid GSTIN format")

    existing = await db.execute(select(GstRegistration).where(GstRegistration.gstin == gstin))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="GSTIN already registered")

    reg = GstRegistration(
        client_id=req.client_id,
        gstin=gstin,
        trade_name=req.trade_name,
        legal_name=req.legal_name,
        address=req.address,
        state_code=req.state_code,
        state_name=req.state_name,
        registration_type=req.registration_type,
        taxpayer_type=req.taxpayer_type,
        constitution=req.constitution,
        registration_date=req.registration_date,
        filing_frequency=req.filing_frequency,
        is_composition=req.is_composition,
        e_invoice_enabled=req.e_invoice_enabled,
        e_waybill_enabled=req.e_waybill_enabled,
        gst_practice_head=req.gst_practice_head,
    )
    db.add(reg)
    await db.commit()
    await db.refresh(reg)
    return reg


@router.get("/registrations/{reg_id}", response_model=GstRegistrationResponse)
async def get_gst_registration(
    reg_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    reg = await db.get(GstRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    client = await db.get(Client, reg.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@router.put("/registrations/{reg_id}", response_model=GstRegistrationResponse)
async def update_gst_registration(
    reg_id: uuid.UUID,
    req: GstRegistrationUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    reg = await db.get(GstRegistration, reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    client = await db.get(Client, reg.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Registration not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(reg, field, value)
    await db.commit()
    await db.refresh(reg)
    return reg


@router.get("/hsn-sac", response_model=list[HsnSacCodeResponse])
async def list_hsn_sac_codes(
    search: str | None = Query(None),
    code_type: str | None = Query(None, alias="type"),
    gst_rate: float | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    query = select(HsnSacCode).where(HsnSacCode.is_active == True)
    if search:
        query = query.where(
            or_(HsnSacCode.code.ilike(f"%{search}%"), HsnSacCode.description.ilike(f"%{search}%"))
        )
    if code_type:
        query = query.where(HsnSacCode.type == code_type)
    if gst_rate is not None:
        query = query.where(HsnSacCode.gst_rate == gst_rate)
    query = query.order_by(HsnSacCode.code)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/hsn-sac", response_model=HsnSacCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_hsn_sac_code(
    req: HsnSacCodeCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(HsnSacCode).where(HsnSacCode.code == req.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="HSN/SAC code already exists")

    half_rate = req.gst_rate / 2
    code = HsnSacCode(
        code=req.code,
        description=req.description,
        type=req.type,
        gst_rate=req.gst_rate,
        cgst_rate=req.cgst_rate if req.cgst_rate is not None else half_rate,
        sgst_rate=req.sgst_rate if req.sgst_rate is not None else half_rate,
        igst_rate=req.igst_rate if req.igst_rate is not None else req.gst_rate,
        cess_rate=req.cess_rate,
        compensation_cess=req.compensation_cess,
        chapter=req.chapter,
        effective_from=req.effective_from,
        effective_to=req.effective_to,
    )
    db.add(code)
    await db.commit()
    await db.refresh(code)
    return code


@router.put("/hsn-sac/{code_id}", response_model=HsnSacCodeResponse)
async def update_hsn_sac_code(
    code_id: uuid.UUID,
    req: HsnSacCodeUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    code = await db.get(HsnSacCode, code_id)
    if not code:
        raise HTTPException(status_code=404, detail="HSN/SAC code not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(code, field, value)
    if req.gst_rate is not None:
        half_rate = req.gst_rate / 2
        if req.cgst_rate is None:
            code.cgst_rate = half_rate
        if req.sgst_rate is None:
            code.sgst_rate = half_rate
        if req.igst_rate is None:
            code.igst_rate = req.gst_rate
    await db.commit()
    await db.refresh(code)
    return code


@router.delete("/hsn-sac/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hsn_sac_code(
    code_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    code = await db.get(HsnSacCode, code_id)
    if not code:
        raise HTTPException(status_code=404, detail="HSN/SAC code not found")
    code.is_active = False
    await db.commit()


@router.post("/compute", response_model=GstComputeResponse)
async def compute_gst_invoice(
    req: GstComputeRequest,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    line_dicts = [line.model_dump() for line in req.lines]
    result = compute_invoice(
        lines=line_dicts,
        is_inter_state=req.is_inter_state,
        seller_state_code=req.seller_state_code,
        customer_state_code=req.customer_state_code,
    )
    return result


@router.get("/invoices", response_model=list[GstInvoiceResponse])
async def list_gst_invoices(
    client_id: uuid.UUID | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(GstInvoice).join(Client, GstInvoice.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(GstInvoice.client_id == client_id)
    if status_filter:
        query = query.where(GstInvoice.status == status_filter)
    query = query.order_by(GstInvoice.invoice_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/invoices", response_model=GstInvoiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_invoice(
    req: GstInvoiceCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    reg = await db.get(GstRegistration, req.gst_registration_id)
    if not reg or reg.client_id != req.client_id:
        raise HTTPException(status_code=404, detail="GST registration not found")

    line_dicts = [line.model_dump() for line in req.lines]
    computed = compute_invoice(
        lines=line_dicts,
        is_inter_state=req.is_inter_state,
        seller_state_code=reg.state_code,
        customer_state_code=req.customer_state_code,
    )

    invoice = GstInvoice(
        client_id=req.client_id,
        gst_registration_id=req.gst_registration_id,
        invoice_number=req.invoice_number,
        invoice_date=req.invoice_date,
        invoice_type=req.invoice_type,
        supply_type=req.supply_type,
        supply_place=req.supply_place,
        is_inter_state=req.is_inter_state,
        customer_name=req.customer_name,
        customer_gstin=req.customer_gstin,
        customer_address=req.customer_address,
        customer_state_code=req.customer_state_code,
        total_taxable_value=computed["total_taxable_value"],
        total_cgst=computed["total_cgst"],
        total_sgst=computed["total_sgst"],
        total_igst=computed["total_igst"],
        total_cess=computed["total_cess"],
        total_invoice_value=computed["total_invoice_value"],
        status="draft",
        notes=req.notes,
    )
    db.add(invoice)
    await db.flush()

    for cl in computed["lines"]:
        line = GstInvoiceLine(
            invoice_id=invoice.id,
            hsn_sac_code=cl["hsn_sac_code"],
            description=cl["description"],
            quantity=cl["quantity"],
            unit_price=cl["unit_price"],
            taxable_value=cl["taxable_value"],
            gst_rate=cl["gst_rate"],
            cgst_rate=cl["cgst_rate"],
            sgst_rate=cl["sgst_rate"],
            igst_rate=cl["igst_rate"],
            cgst_amount=cl["cgst_amount"],
            sgst_amount=cl["sgst_amount"],
            igst_amount=cl["igst_amount"],
            cess_amount=cl["cess_amount"],
            total_amount=cl["total_amount"],
            sort_order=cl["sort_order"],
        )
        db.add(line)

    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}", response_model=GstInvoiceDetailResponse)
async def get_gst_invoice(
    invoice_id: uuid.UUID,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    invoice = await db.get(GstInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    client = await db.get(Client, invoice.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Invoice not found")

    lines_result = await db.execute(
        select(GstInvoiceLine).where(GstInvoiceLine.invoice_id == invoice_id).order_by(GstInvoiceLine.sort_order)
    )
    lines = lines_result.scalars().all()
    return GstInvoiceDetailResponse(
        **invoice.__dict__,
        lines=lines,
    )


@router.put("/invoices/{invoice_id}", response_model=GstInvoiceResponse)
async def update_gst_invoice(
    invoice_id: uuid.UUID,
    req: GstInvoiceUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    invoice = await db.get(GstInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    client = await db.get(Client, invoice.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.get("/returns", response_model=list[GstReturnResponse])
async def list_gst_returns(
    client_id: uuid.UUID | None = Query(None),
    return_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(GstReturn).join(Client, GstReturn.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(GstReturn.client_id == client_id)
    if return_type:
        query = query.where(GstReturn.return_type == return_type)
    if status_filter:
        query = query.where(GstReturn.status == status_filter)
    query = query.order_by(GstReturn.return_period.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/returns", response_model=GstReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_return(
    req: GstReturnCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    reg = await db.get(GstRegistration, req.gst_registration_id)
    if not reg or reg.client_id != req.client_id:
        raise HTTPException(status_code=404, detail="GST registration not found")

    gst_return = GstReturn(
        client_id=req.client_id,
        gst_registration_id=req.gst_registration_id,
        return_type=req.return_type,
        financial_year=req.financial_year,
        return_period=req.return_period,
        due_date=req.due_date,
    )
    db.add(gst_return)
    await db.commit()
    await db.refresh(gst_return)
    return gst_return


@router.put("/returns/{return_id}", response_model=GstReturnResponse)
async def update_gst_return(
    return_id: uuid.UUID,
    req: GstReturnUpdate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    gst_return = await db.get(GstReturn, return_id)
    if not gst_return:
        raise HTTPException(status_code=404, detail="GST return not found")
    client = await db.get(Client, gst_return.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="GST return not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(gst_return, field, value)
    await db.commit()
    await db.refresh(gst_return)
    return gst_return
