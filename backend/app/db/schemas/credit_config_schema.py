from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum
from app.db.models.credit_model import LifecycleStatus





class CreditConfigBase(BaseModel):
    config_key: str = Field(..., max_length=50)
    config_value: Dict[str, Any]
    description: Optional[str] = None
    status: Optional[LifecycleStatus] = LifecycleStatus.active


class CreditConfigCreate(CreditConfigBase):
    pass


class CreditConfigUpdate(BaseModel):
    config_key: Optional[str] = None
    config_value: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    status: Optional[LifecycleStatus] = None


class CreditConfigResponse(CreditConfigBase):
    creditid: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
