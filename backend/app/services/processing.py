from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..classifier.heuristic import HeuristicClassifier
from ..gmail.adapter import NormalizedEmail
from ..models import Classification, EmailMetadata, ProcessingEvent, UserSettings, Category
from ..rules.engine import evaluate_rules


def _event(db: Session, email_id: int, event_type: str, status: str, error: str | None = None) -> None:
    db.add(ProcessingEvent(email_id=email_id, event_type=event_type, status=status, error_message=error))


def process_email(db: Session, user_id: int, account_id: int, email: NormalizedEmail, classifier=None) -> EmailMetadata:
    """Persist a single Gmail message exactly once; sending is only attempted after persistence."""
    existing = db.scalar(select(EmailMetadata).where(EmailMetadata.gmail_account_id == account_id,
        EmailMetadata.gmail_message_id == email.message_id))
    if existing:
        return existing
    metadata = EmailMetadata(user_id=user_id, gmail_account_id=account_id, gmail_message_id=email.message_id,
        gmail_thread_id=email.thread_id, sender=email.sender, subject=email.subject, received_at=email.received_at)
    db.add(metadata)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return db.scalar(select(EmailMetadata).where(EmailMetadata.gmail_account_id == account_id,
            EmailMetadata.gmail_message_id == email.message_id))
    _event(db, metadata.id, "RECEIVED", "completed")
    result = evaluate_rules(db, user_id, email) or (classifier or HeuristicClassifier()).classify(email)
    db.add(Classification(email_id=metadata.id, category=result.category, confidence=result.confidence,
        reason=result.reason, model=result.model))
    metadata.processed_at = datetime.utcnow()
    _event(db, metadata.id, "CLASSIFIED", "completed")
    # Actual Gmail API forwarding is wired only after OAuth credentials are available.
    settings = db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
    if result.category in (Category.IMPORTANT, Category.URGENT) and settings and settings.destination_email:
        _event(db, metadata.id, "FORWARDING_STARTED", "pending")
    db.commit()
    db.refresh(metadata)
    return metadata
