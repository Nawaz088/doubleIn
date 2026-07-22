import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.models.organization import User
from app.models.accounting import Client
from app.models.integrations_india import (
    IndianBankConnection, UpiTransaction,
    ZohoBooksIntegration, TallyIntegration,
)
from pydantic import BaseModel

router = APIRouter()


# --- Indian Bank Connection ---

class BankConnectionCreate(BaseModel):
    client_id: uuid.UUID
    provider: str
    account_number: str
    account_name: str
    ifsc_code: str
    bank_name: str
    branch_name: Optional[str] = None
    account_type: str = "savings"
    upi_id: Optional[str] = None
    is_primary: bool = False


class BankConnectionResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    provider: str
    account_number: str
    account_name: str
    ifsc_code: str
    bank_name: str
    branch_name: Optional[str] = None
    account_type: str
    upi_id: Optional[str] = None
    is_primary: bool
    is_active: bool
    last_synced_at: Optional[str] = None

    model_config = {"from_attributes": True}


class UpiTransactionResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    upi_transaction_id: str
    upi_ref_number: Optional[str] = None
    payer_vpa: Optional[str] = None
    payee_vpa: Optional[str] = None
    amount: float
    transaction_date: str
    transaction_type: str
    remark: Optional[str] = None
    status: str
    payment_method: Optional[str] = None

    model_config = {"from_attributes": True}


class ZohoBooksConnect(BaseModel):
    client_id: uuid.UUID
    organization_id: str
    organization_name: str
    zoho_email: str
    access_token: str
    refresh_token: str
    token_expires_at: str


class ZohoBooksResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    client_id: Optional[uuid.UUID] = None
    organization_id: str
    organization_name: str
    zoho_email: str
    is_active: bool
    last_sync_at: Optional[str] = None

    model_config = {"from_attributes": True}


class TallyConnect(BaseModel):
    name: str
    tally_company_name: str
    connection_type: str = "xml"
    tally_host: str = "localhost"
    tally_port: int = 9000
    sync_config: Optional[dict] = None


class TallyResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    tally_company_name: str
    connection_type: str
    tally_host: str
    tally_port: int
    is_active: bool
    last_sync_at: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/bank-connections", response_model=list[BankConnectionResponse])
async def list_bank_connections(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(IndianBankConnection).join(Client, IndianBankConnection.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(IndianBankConnection.client_id == client_id)
    query = query.order_by(IndianBankConnection.is_primary.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/bank-connections", response_model=BankConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_connection(
    req: BankConnectionCreate,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    bc = IndianBankConnection(**req.model_dump())
    if req.is_primary:
        await db.execute(
            select(IndianBankConnection).where(
                IndianBankConnection.client_id == req.client_id,
                IndianBankConnection.is_primary == True,
            )
        )
    db.add(bc)
    await db.commit()
    await db.refresh(bc)
    return bc


@router.get("/upi-transactions", response_model=list[UpiTransactionResponse])
async def list_upi_transactions(
    client_id: uuid.UUID | None = Query(None),
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(UpiTransaction).join(Client, UpiTransaction.client_id == Client.id).where(Client.org_id == user.org_id)
    if client_id:
        query = query.where(UpiTransaction.client_id == client_id)
    query = query.order_by(UpiTransaction.transaction_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/zoho-books/connect", response_model=ZohoBooksResponse)
async def connect_zoho_books(
    req: ZohoBooksConnect,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    client = await db.get(Client, req.client_id)
    if not client or client.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Client not found")

    integration = ZohoBooksIntegration(
        org_id=user.org_id,
        client_id=req.client_id,
        access_token=req.access_token,
        refresh_token=req.refresh_token,
        token_expires_at=req.token_expires_at,
        organization_id=req.organization_id,
        organization_name=req.organization_name,
        zoho_email=req.zoho_email,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/zoho-books", response_model=list[ZohoBooksResponse])
async def list_zoho_books(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(ZohoBooksIntegration).where(ZohoBooksIntegration.org_id == user.org_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/tally/connect", response_model=TallyResponse)
async def connect_tally(
    req: TallyConnect,
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    integration = TallyIntegration(
        org_id=user.org_id,
        name=req.name,
        tally_company_name=req.tally_company_name,
        connection_type=req.connection_type,
        tally_host=req.tally_host,
        tally_port=req.tally_port,
        sync_config=req.sync_config,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/tally", response_model=list[TallyResponse])
async def list_tally(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    query = select(TallyIntegration).where(TallyIntegration.org_id == user.org_id)
    result = await db.execute(query)
    return result.scalars().all()
