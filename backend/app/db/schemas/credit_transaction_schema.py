from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal


# ──────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class CreditType(str, Enum):
    paid = "paid"
    free = "free"
    used = "used"


# ──────────────────────────────────────────────────────────────
# Base schema
# ──────────────────────────────────────────────────────────────
class CreditTransactionBase(BaseModel):
    userid: int
    amount: int = Field(..., gt=0)
    credit_type: CreditType = CreditType.paid
    reason: Optional[str] = None
    packid: Optional[str] = None
    amount_paid_usd: Optional[Decimal] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    status: Optional[str] = "pending"
    remarks: Optional[str] = None


# ──────────────────────────────────────────────────────────────
# Create / Update
# ──────────────────────────────────────────────────────────────
class CreditTransactionCreate(CreditTransactionBase):
    pass


class CreditTransactionUpdate(BaseModel):
    amount: Optional[int] = None
    credit_type: Optional[CreditType] = None
    reason: Optional[str] = None
    packid: Optional[str] = None
    amount_paid_usd: Optional[Decimal] = None
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    is_deleted: Optional[bool] = None


# ──────────────────────────────────────────────────────────────
# Response
# ──────────────────────────────────────────────────────────────
class CreditTransactionResponse(CreditTransactionBase):
    transactionid: int
    created_at: datetime
    is_deleted: bool = False

    class Config:
        from_attributes = True
