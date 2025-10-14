from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class AccessLevel(str, Enum):
    none = "none"
    read = "read"
    write = "write"
    full = "full"

class AccessControlBase(BaseModel):
    module_key: str = Field(..., max_length=100)
    module_desc: Optional[str] = None
    user_access: Optional[AccessLevel] = AccessLevel.none
    admin_access: Optional[AccessLevel] = AccessLevel.none
    superadmin_access: Optional[AccessLevel] = AccessLevel.none
    is_critical: Optional[bool] = False
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class AccessControlCreate(AccessControlBase):
    pass

class AccessControlUpdate(BaseModel):
    module_desc: Optional[str] = None
    user_access: Optional[AccessLevel] = None
    admin_access: Optional[AccessLevel] = None
    superadmin_access: Optional[AccessLevel] = None
    is_critical: Optional[bool] = None
    status: Optional[LifecycleStatus] = None

class AccessControlResponse(AccessControlBase):
    accessid: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
