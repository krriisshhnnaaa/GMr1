from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .deps import current_user
from ..database import get_db
from ..models import Category, Classification, EmailMetadata, GmailAccount, User, UserRule, UserSettings
from ..schemas import AccountOut, EmailOut, RuleIn, RuleOut, SettingsIn, SettingsOut

router = APIRouter(prefix="/api")

@router.get("/health")
def health(): return {"status": "ok"}

@router.get("/accounts", response_model=list[AccountOut])
def accounts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(GmailAccount).where(GmailAccount.user_id == user.id, GmailAccount.active)).all()

@router.delete("/accounts/{account_id}", status_code=204)
def disconnect(account_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    account = db.scalar(select(GmailAccount).where(GmailAccount.id == account_id, GmailAccount.user_id == user.id))
    if not account: raise HTTPException(404, "Account not found")
    account.active = False
    db.commit()

@router.get("/settings", response_model=SettingsOut)
def settings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(UserSettings).where(UserSettings.user_id == user.id))
    return SettingsOut(destination_email=item.destination_email if item else None)

@router.put("/settings", response_model=SettingsOut)
def update_settings(payload: SettingsIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(UserSettings).where(UserSettings.user_id == user.id))
    if not item:
        item = UserSettings(user_id=user.id)
        db.add(item)
    item.destination_email = str(payload.destination_email) if payload.destination_email else None
    db.commit()
    return SettingsOut(destination_email=item.destination_email)

@router.get("/rules", response_model=list[RuleOut])
def rules(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(UserRule).where(UserRule.user_id == user.id)).all()

@router.post("/rules", response_model=RuleOut, status_code=201)
def create_rule(payload: RuleIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = UserRule(user_id=user.id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.delete("/rules/{rule_id}", status_code=204)
def delete_rule(rule_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(UserRule).where(UserRule.id == rule_id, UserRule.user_id == user.id))
    if not item: raise HTTPException(404, "Rule not found")
    db.delete(item); db.commit()

@router.get("/emails", response_model=list[EmailOut])
def emails(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(EmailMetadata, Classification).outerjoin(Classification).where(EmailMetadata.user_id == user.id).order_by(EmailMetadata.received_at.desc()).limit(100)).all()
    return [EmailOut(id=e.id, sender=e.sender, subject=e.subject, received_at=e.received_at, processed_at=e.processed_at, forwarded_at=e.forwarded_at, category=c.category if c else None, confidence=c.confidence if c else None) for e,c in rows]

@router.get("/emails/{email_id}", response_model=EmailOut)
def email(email_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.execute(select(EmailMetadata, Classification).outerjoin(Classification).where(EmailMetadata.id == email_id, EmailMetadata.user_id == user.id)).first()
    if not row: raise HTTPException(404, "Email not found")
    e,c = row
    return EmailOut(id=e.id, sender=e.sender, subject=e.subject, received_at=e.received_at, processed_at=e.processed_at, forwarded_at=e.forwarded_at, category=c.category if c else None, confidence=c.confidence if c else None)

@router.get("/stats")
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=1)
    rows = db.execute(select(Classification.category, func.count()).join(EmailMetadata).where(EmailMetadata.user_id == user.id, EmailMetadata.created_at >= since).group_by(Classification.category)).all()
    counts = {category.value: count for category, count in rows}
    return {"processed_today": sum(counts.values()), "categories": {c.value: counts.get(c.value, 0) for c in Category}}
#change
