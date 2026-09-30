import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parseaddr


@dataclass
class NormalizedEmail:
    message_id: str
    thread_id: str
    sender: str
    recipients: list[str]
    subject: str
    body_text: str
    body_html: str | None
    received_at: datetime
    labels: list[str]
    has_attachments: bool


def _headers(message: dict) -> dict[str, str]:
    return {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}


def _part_body(part: dict, mime: str) -> str | None:
    if part.get("mimeType") == mime and part.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(part["body"]["data"] + "===").decode(errors="replace")
    for child in part.get("parts", []):
        result = _part_body(child, mime)
        if result is not None:
            return result
    return None


def normalize_gmail_message(message: dict) -> NormalizedEmail:
    headers = _headers(message)
    payload = message.get("payload", {})
    sender = parseaddr(headers.get("from", ""))[1] or headers.get("from", "")
    recipients = [x.strip() for x in headers.get("to", "").split(",") if x.strip()]
    text = _part_body(payload, "text/plain") or ""
    html = _part_body(payload, "text/html")
    parts = payload.get("parts", [])
    attachments = any(p.get("filename") for p in parts)
    return NormalizedEmail(message_id=message["id"], thread_id=message.get("threadId", ""), sender=sender,
        recipients=recipients, subject=headers.get("subject", ""), body_text=text, body_html=html,
        received_at=datetime.fromtimestamp(int(message.get("internalDate", 0)) / 1000, tz=timezone.utc),
        labels=message.get("labelIds", []), has_attachments=attachments)
