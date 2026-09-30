from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.gmail.adapter import NormalizedEmail
from app.models import Category, GmailAccount, User, UserSettings
from app.services.processing import process_email


def email(message_id="m1"):
    return NormalizedEmail(message_id=message_id, thread_id="t1", sender="client@example.com", recipients=["me@example.com"],
        subject="Project deadline today", body_text="Action required immediately", body_html=None,
        received_at=datetime.now(timezone.utc), labels=["INBOX"], has_attachments=False)


def test_processing_is_idempotent_and_classifies_urgent():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    user = User(email="me@example.com"); db.add(user); db.flush()
    account = GmailAccount(user_id=user.id, email_address="me@example.com"); db.add(account); db.flush()
    db.add(UserSettings(user_id=user.id, destination_email="dest@example.com")); db.commit()
    first = process_email(db, user.id, account.id, email())
    second = process_email(db, user.id, account.id, email())
    assert first.id == second.id
    assert first.classification.category == Category.URGENT
