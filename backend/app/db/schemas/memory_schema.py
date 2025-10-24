from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ---------- ENUM ----------
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


# ---------- BASE ----------
class MemoryBase(BaseModel):
    memorycontent: str
    agentid: int
    projectid: int
    status: Optional[LifecycleStatus] = LifecycleStatus.active


# ---------- CREATE ----------
class MemoryCreate(MemoryBase):
    pass


# ---------- UPDATE ----------
class MemoryUpdate(BaseModel):
    memorycontent: Optional[str] = None
    status: Optional[LifecycleStatus] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


# ---------- RESPONSE ----------
class MemoryResponse(MemoryBase):
    memoryid: int
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
