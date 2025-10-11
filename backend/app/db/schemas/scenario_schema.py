from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ScenarioBase(BaseModel):
    scenarioName: str = Field(..., max_length=100)
    scenarioPrompt: str
    projectID: int
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioUpdate(BaseModel):
    scenarioName: Optional[str] = Field(None, max_length=100)
    scenarioPrompt: Optional[str] = None
    status: Optional[LifecycleStatus] = None

class ScenarioResponse(ScenarioBase):
    scenarioID: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
