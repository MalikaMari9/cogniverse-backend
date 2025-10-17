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
    agentname: Annotated[str, Field(min_length=1, max_length=100)]
    agentpersonality: Optional[str] = Field(None, max_length=20)
    agentskill: List[str] = Field(default_factory=list)  # ✅ relaxed
    agentbiography: Optional[str] = None
    agentconstraints: List[str] = Field(default_factory=list)  # ✅ relaxed
    agentquirk: List[str] = Field(default_factory=list)
    agentmotivation: Optional[str] = None
    userid: Optional[int] = None  # ✅ backend will inject
    status: Optional[LifecycleStatus] = LifecycleStatus.active


# ---------- CREATE SCHEMA ----------
class AgentCreate(AgentBase):
    pass


# ---------- UPDATE SCHEMA ----------
class AgentUpdate(BaseModel):
    agentname: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    agentpersonality: Optional[Annotated[str, Field(max_length=20)]] = None
    agentskill: Optional[List[str]] = None
    agentbiography: Optional[str] = None
    agentconstraints: Optional[List[str]] = None
    agentquirk: Optional[List[str]] = None
    agentmotivation: Optional[str] = None
    status: Optional[LifecycleStatus] = None


# ---------- RESPONSE SCHEMA ----------
class AgentResponse(AgentBase):
    agentid: int
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True
