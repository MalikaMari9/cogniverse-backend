from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class SystemLogBase(BaseModel):
    action_type: str = Field(..., max_length=100)
    userid: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    browser_info: Optional[str] = Field(None, max_length=200)
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class SystemLogCreate(SystemLogBase):
    pass

class SystemLogResponse(SystemLogBase):
    logid: int
    created_at: datetime
    username: Optional[str] = None  # Add username field

    class Config:
        from_attributes = True
