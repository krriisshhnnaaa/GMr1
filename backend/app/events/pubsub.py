import base64
import json
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/events", tags=["events"])

@router.post("/gmail-pubsub")
async def gmail_pubsub(request: Request):
    """Pub/Sub push receiver. Configure authenticated push/OIDC validation before public deployment."""
    envelope = await request.json()
    message = envelope.get("message", {})
    if not message.get("data"):
        raise HTTPException(400, "Invalid Pub/Sub envelope")
    try:
        notification = json.loads(base64.b64decode(message["data"]).decode())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(400, "Invalid Pub/Sub data")
    # Gmail notification contains emailAddress/historyId, never email content. A worker must call
    # Gmail history.list then messages.get and hand each normalized message to process_email.
    return {"status": "accepted", "email_address": notification.get("emailAddress"), "history_id": notification.get("historyId")}
