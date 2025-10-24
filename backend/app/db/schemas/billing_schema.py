from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum

# ──────────────────────────────────────────────────────────────
# Shared Enums
# ──────────────────────────────────────────────────────────────
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

# ──────────────────────────────────────────────────────────────
# Base Schema
# ──────────────────────────────────────────────────────────────
class BillingBase(BaseModel):
    userid: int
    paid_credits: Optional[int] = Field(default=0, ge=0)
    free_credits: Optional[int] = Field(default=5, ge=0)
    last_free_credit_date: Optional[date] = None
    status: Optional[LifecycleStatus] = LifecycleStatus.active

# ──────────────────────────────────────────────────────────────
# Create / Update
# ──────────────────────────────────────────────────────────────
class BillingCreate(BillingBase):
    pass

class BillingUpdate(BaseModel):
    paid_credits: Optional[int] = Field(default=None, ge=0)
    free_credits: Optional[int] = Field(default=None, ge=0)
    last_free_credit_date: Optional[date] = None
    status: Optional[LifecycleStatus] = None
    is_deleted: Optional[bool] = None

# ──────────────────────────────────────────────────────────────
# Response
# ──────────────────────────────────────────────────────────────
class BillingResponse(BillingBase):
    billingid: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool = False
    total_credits: int

    class Config:
        from_attributes = True
