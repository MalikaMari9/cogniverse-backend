from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RevokedTokenBase(BaseModel):
    token: str
    user_id: Optional[int] = None

class RevokedTokenCreate(RevokedTokenBase):
    pass

class RevokedTokenResponse(RevokedTokenBase):
    id: int
    revoked_at: datetime

    class Config:
        orm_mode = True
