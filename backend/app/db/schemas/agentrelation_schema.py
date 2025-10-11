from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class AgentRelationBase(BaseModel):
    projectID: int
    agentA_ID: int
    agentB_ID: int
    relationAtoB: int = Field(..., ge=-100, le=100)
    relationBtoA: int = Field(..., ge=-100, le=100)
    return_state: bool = False
    status: LifecycleStatus = LifecycleStatus.active


class AgentRelationCreate(AgentRelationBase):
    pass


class AgentRelationUpdate(BaseModel):
    relationAtoB: Optional[int] = Field(None, ge=-100, le=100)
    relationBtoA: Optional[int] = Field(None, ge=-100, le=100)
    return_state: Optional[bool] = None
    status: Optional[LifecycleStatus] = None


class AgentRelationResponse(AgentRelationBase):
    agentRelationID: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True
