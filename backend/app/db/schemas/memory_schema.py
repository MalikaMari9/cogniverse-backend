from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------- Base ----------
class MemoryBase(BaseModel):
    memorycontent: str
    agentid: int
    projectid: int


# ---------- Create ----------
class MemoryCreate(MemoryBase):
    pass


# ---------- Update ----------
class MemoryUpdate(BaseModel):
    memorycontent: Optional[str]
    status: Optional[str]


# ---------- Response ----------
class MemoryResponse(MemoryBase):
    memoryid: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
