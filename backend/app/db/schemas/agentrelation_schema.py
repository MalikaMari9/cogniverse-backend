from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class AgentRelationBase(BaseModel):
    projectid: int
    agenta_id: int
    agentb_id: int
    relationatob: int = Field(..., ge=-100, le=100)
    relationbtoa: int = Field(..., ge=-100, le=100)
    return_state: bool = False
    status: LifecycleStatus = LifecycleStatus.active


class AgentRelationCreate(AgentRelationBase):
    pass


class AgentRelationUpdate(BaseModel):
    relationatob: Optional[int] = Field(None, ge=-100, le=100)
    relationbtoa: Optional[int] = Field(None, ge=-100, le=100)
    return_state: Optional[bool] = None
    status: Optional[LifecycleStatus] = None


class AgentRelationResponse(AgentRelationBase):
    agentrelationid: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True