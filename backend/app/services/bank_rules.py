import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank import BankTransaction, ClassificationRule


async def apply_rules_to_transaction(
    db: AsyncSession,
    transaction: BankTransaction,
) -> Optional[ClassificationRule]:
    rules_result = await db.execute(
        select(ClassificationRule)
        .where(
            ClassificationRule.client_id == transaction.bank_connection_id,
            ClassificationRule.is_active == True,
        )
        .order_by(ClassificationRule.priority.desc())
    )
    rules = rules_result.scalars().all()

    for rule in rules:
        conditions = rule.conditions or {}
        matched = True

        if "contains" in conditions:
            if conditions["contains"].lower() not in (transaction.description or "").lower():
                matched = False
        if "vendor_contains" in conditions:
            if conditions["vendor_contains"].lower() not in (transaction.vendor_name or "").lower():
                matched = False
        if "amount_equals" in conditions:
            if float(transaction.amount) != float(conditions["amount_equals"]):
                matched = False
        if "amount_range" in conditions:
            r = conditions["amount_range"]
            if not (r.get("min", float("-inf")) <= float(transaction.amount) <= r.get("max", float("inf"))):
                matched = False

        if matched:
            actions = rule.actions or {}
            if "category" in actions:
                transaction.category = actions["category"]
            if "status" in actions:
                transaction.status = actions["status"]
            if "classification_tier" in actions:
                transaction.classification_tier = actions["classification_tier"]
            return rule

    return None


async def auto_classify_all(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> int:
    from app.models.bank import BankConnection

    connections_result = await db.execute(
        select(BankConnection).where(
            BankConnection.client_id == client_id,
            BankConnection.is_active == True,
        )
    )
    connections = connections_result.scalars().all()

    classified = 0
    for conn in connections:
        txns_result = await db.execute(
            select(BankTransaction).where(
                BankTransaction.bank_connection_id == conn.id,
                BankTransaction.classification_tier == "unclassified",
            )
        )
        txns = txns_result.scalars().all()

        for txn in txns:
            rule = await apply_rules_to_transaction(db, txn)
            if rule:
                classified += 1

    return classified
