from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ConfigBase(BaseModel):
    config_key: str = Field(..., max_length=100)
    config_value: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class ConfigCreate(ConfigBase):
    pass

class ConfigUpdate(BaseModel):
    config_key: Optional[str] = None
    config_value: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LifecycleStatus] = None

class ConfigResponse(ConfigBase):
    configid: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
