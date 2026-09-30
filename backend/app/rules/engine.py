from sqlalchemy import select
from sqlalchemy.orm import Session
from ..classifier.base import ClassificationResult
from ..gmail.adapter import NormalizedEmail
from ..models import UserRule


def evaluate_rules(db: Session, user_id: int, email: NormalizedEmail) -> ClassificationResult | None:
    for rule in db.scalars(select(UserRule).where(UserRule.user_id == user_id)):
        matched = rule.value.lower() == email.sender.lower() if rule.kind == "sender" else email.sender.lower().endswith("@" + rule.value.lower())
        if matched:
            return ClassificationResult(rule.category, 1.0, f"Matched {rule.kind} rule.", "rule-engine")
    return None
