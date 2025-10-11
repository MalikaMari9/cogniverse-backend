from pydantic import BaseModel, Field
from typing import List, Optional
from typing_extensions import Annotated
from datetime import datetime
from enum import Enum


# ---------- ENUM ----------
class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


# ---------- BASE SCHEMA ----------
class AgentBase(BaseModel):
    agentName: Annotated[str, Field(min_length=1, max_length=100)]
    agentPersonality: Optional[str] = Field(None, max_length=20)
    agentSkill: Annotated[List[str], Field(min_length=1, description="Must include at least one skill")]
    agentBiography: Optional[str] = None
    agentConstraints: Annotated[List[str], Field(min_length=1, description="Must include at least one constraint")]
    agentQuirk: Optional[List[str]] = Field(default_factory=list)
    agentMotivation: Optional[str] = None
    userID: int
    status: Optional[LifecycleStatus] = LifecycleStatus.active


# ---------- CREATE SCHEMA ----------
class AgentCreate(AgentBase):
    pass


# ---------- UPDATE SCHEMA ----------
class AgentUpdate(BaseModel):
    agentName: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    agentPersonality: Optional[Annotated[str, Field(max_length=20)]] = None
    agentSkill: Optional[Annotated[List[str], Field(min_length=1)]] = None
    agentBiography: Optional[str] = None
    agentConstraints: Optional[Annotated[List[str], Field(min_length=1)]] = None
    agentQuirk: Optional[List[str]] = None
    agentMotivation: Optional[str] = None
    status: Optional[LifecycleStatus] = None


# ---------- RESPONSE SCHEMA ----------
class AgentResponse(AgentBase):
    agentID: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
