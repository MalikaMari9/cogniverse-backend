from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class ProjectAgentBase(BaseModel):
    projectID: int
    agentID: int
    agentSnapshot: Optional[Any] = None
    status: LifecycleStatus = LifecycleStatus.active


class ProjectAgentCreate(ProjectAgentBase):
    pass


class ProjectAgentUpdate(BaseModel):
    agentSnapshot: Optional[Any] = None
    status: Optional[LifecycleStatus] = None


class ProjectAgentResponse(ProjectAgentBase):
    projAgentID: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode = True
