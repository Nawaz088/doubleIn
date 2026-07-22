import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank import BankConnection, BankTransaction
from app.models.accounting import Client
from app.models.misc import Integration, SyncLog


async def sync_qbo_chart_of_accounts(
    db: AsyncSession,
    integration: Integration,
    client_id: uuid.UUID,
) -> int:
    from app.services.integrations.qbo import qbo_api_request
    from app.services.token_crypto import decrypt_token

    access_token = decrypt_token(integration.access_token)
    realm_id = integration.realm_id

    try:
        resp = await qbo_api_request(
            integration, "GET", "account",
            params={"minorversion": 65}
        )
        accounts = resp.get("QueryResponse", {}).get("Account", [])
        return len(accounts)
    except Exception as e:
        return 0


async def sync_qbo_transactions(
    db: AsyncSession,
    integration: Integration,
    client_id: uuid.UUID,
) -> int:
    from app.services.integrations.qbo import qbo_api_request
    from app.services.token_crypto import decrypt_token

    try:
        purchases_resp = await qbo_api_request(
            integration, "GET", "purchase",
            params={"minorversion": 65, "maxresults": 1000}
        )
        purchases = purchases_resp.get("QueryResponse", {}).get("Purchase", [])

        bills_resp = await qbo_api_request(
            integration, "GET", "bill",
            params={"minorversion": 65, "maxresults": 1000}
        )
        bills = bills_resp.get("QueryResponse", {}).get("Bill", [])

        return len(purchases) + len(bills)
    except Exception:
        return 0


async def sync_qbo_vendors(
    db: AsyncSession,
    integration: Integration,
    client_id: uuid.UUID,
) -> int:
    from app.services.integrations.qbo import qbo_api_request

    try:
        resp = await qbo_api_request(
            integration, "GET", "vendor",
            params={"minorversion": 65, "maxresults": 1000}
        )
        vendors = resp.get("QueryResponse", {}).get("Vendor", [])
        return len(vendors)
    except Exception:
        return 0


async def sync_qbo_customers(
    db: AsyncSession,
    integration: Integration,
    client_id: uuid.UUID,
) -> int:
    from app.services.integrations.qbo import qbo_api_request

    try:
        resp = await qbo_api_request(
            integration, "GET", "customer",
            params={"minorversion": 65, "maxresults": 1000}
        )
        customers = resp.get("QueryResponse", {}).get("Customer", [])
        return len(customers)
    except Exception:
        return 0


async def push_journal_entry_to_qbo(
    db: AsyncSession,
    integration: Integration,
    journal_entry_id: uuid.UUID,
) -> Optional[str]:
    from app.services.integrations.qbo import qbo_api_request
    from app.models.bank import JournalEntry, JournalEntryLine

    je = await db.get(JournalEntry, journal_entry_id)
    if not je:
        return None

    lines = []
    for line in je.lines:
        lines.append({
            "Description": line.description or "",
            "Amount": float(line.debit_amount - line.credit_amount),
            "PostingType": "Debit" if line.debit_amount > 0 else "Credit",
        })

    payload = {
        "TxnDate": str(je.date),
        "PrivateNote": je.description or "",
        "Line": lines,
    }

    try:
        resp = await qbo_api_request(integration, "POST", "journalentry", json_body=payload)
        external_id = resp.get("JournalEntry", {}).get("Id")
        return external_id
    except Exception:
        return None
