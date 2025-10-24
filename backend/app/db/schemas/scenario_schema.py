from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ScenarioBase(BaseModel):
    scenarioname: str = Field(..., max_length=100)
    scenarioprompt: str
    projectid: int
    status: Optional[LifecycleStatus] = LifecycleStatus.active
 
class ScenarioCreate(ScenarioBase):
    pass

class ScenarioUpdate(BaseModel):
    scenarioname: Optional[str] = Field(None, max_length=100)
    scenarioprompt: Optional[str] = None
    status: Optional[LifecycleStatus] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None

class ScenarioResponse(ScenarioBase):
    scenarioid: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True