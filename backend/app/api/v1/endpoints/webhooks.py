from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.post("/qbo")
async def qbo_webhook(request: Request):
    body = await request.json()
    event = body.get("eventNotifications", [{}])[0]
    realm_id = event.get("realmId")
    entity_type = event.get("dataChangeEvent", {}).get("entities", [{}])[0].get("name")

    return {"status": "received", "realm_id": realm_id, "entity_type": entity_type}


@router.post("/xero")
async def xero_webhook(request: Request):
    body = await request.json()
    return {"status": "received", "events": body.get("events", [])}


@router.post("/sendgrid")
async def sendgrid_webhook(request: Request):
    body = await request.json()
    emails = body if isinstance(body, list) else [body]
    return {"status": "received", "count": len(emails)}
