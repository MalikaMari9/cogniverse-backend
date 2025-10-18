from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class ProjectAgentBase(BaseModel):
    projectid: int
    agentid: int
    agentsnapshot: Optional[Any] = None
    status: LifecycleStatus = LifecycleStatus.active


class ProjectAgentCreate(ProjectAgentBase):
    pass


class ProjectAgentUpdate(BaseModel):
    agentsnapshot: Optional[Any] = None
    status: Optional[LifecycleStatus] = None


class ProjectAgentResponse(ProjectAgentBase):
    projagentid: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True