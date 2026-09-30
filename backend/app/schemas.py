from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from .models import Category


class AccountOut(BaseModel):
    id: int
    email_address: EmailStr
    active: bool
    model_config = {"from_attributes": True}


class SettingsIn(BaseModel):
    destination_email: EmailStr | None = None


class SettingsOut(SettingsIn):
    pass


class RuleIn(BaseModel):
    kind: str = Field(pattern="^(sender|domain)$")
    value: str = Field(min_length=1, max_length=512)
    category: Category


class RuleOut(RuleIn):
    id: int
    model_config = {"from_attributes": True}


class EmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    received_at: datetime
    processed_at: datetime | None
    forwarded_at: datetime | None
    category: Category | None = None
    confidence: float | None = None
    model_config = {"from_attributes": True}
