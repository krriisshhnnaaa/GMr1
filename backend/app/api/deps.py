from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User


def current_user(x_user_email: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    """Prototype identity boundary; production should replace this with a signed app session."""
    if not x_user_email:
        raise HTTPException(401, "Missing X-User-Email")
    user = db.scalar(select(User).where(User.email == x_user_email.lower()))
    if not user:
        user = User(email=x_user_email.lower())
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
