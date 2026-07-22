from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    scorecards,
    clients,
    tasks,
    task_lists,
    bank,
    journal,
    reports,
    file_review,
    portal,
    tax,
    receipts,
    accruals,
    inbox,
    integrations,
    org,
    users,
    files,
    webhooks,
    gst,
    accounting_india,
    integrations_india,
    tds,
    itr,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(scorecards.router, prefix="/scorecards", tags=["scorecards"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(task_lists.router, prefix="/task-lists", tags=["task-lists"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(bank.router, prefix="/bank-feeds", tags=["bank-feeds"])
api_router.include_router(journal.router, prefix="/journal-entries", tags=["journal-entries"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(file_review.router, prefix="/file-review", tags=["file-review"])
api_router.include_router(portal.router, prefix="/portal", tags=["portal"])
api_router.include_router(tax.router, prefix="/tax", tags=["tax"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(accruals.router, prefix="/accruals", tags=["accruals"])
api_router.include_router(inbox.router, prefix="/inbox", tags=["inbox"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(org.router, prefix="/org", tags=["org"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(gst.router, prefix="/gst", tags=["gst"])
api_router.include_router(accounting_india.router, prefix="/india", tags=["india"])
api_router.include_router(integrations_india.router, prefix="/india/integrations", tags=["india-integrations"])
api_router.include_router(tds.router, prefix="/tds", tags=["tds"])
api_router.include_router(itr.router, prefix="/itr", tags=["itr"])
