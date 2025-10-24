from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------- Base ----------
class WeaverBase(BaseModel):
    weavercontent: str
    agentid: int
    projectid: int
 


# ---------- Create ----------
class WeaverCreate(WeaverBase):
    pass


# ---------- Update ----------
class WeaverUpdate(BaseModel):
    weavercontent: Optional[str]
    status: Optional[str]
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None



# ---------- Response ----------
class WeaverResponse(WeaverBase):
    weaverid: int
    status: str
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None


    class Config:
        from_attributes = True
