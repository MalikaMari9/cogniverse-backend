from pydantic import BaseModel, Field, validator
from typing import List, Optional


class AgentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    skills: List[str] = Field(..., min_items=1, description="List of skills")
    constraints: List[str] = Field(..., min_items=1, description="List of constraints")
    quirks: Optional[List[str]] = Field(default_factory=list, description="List of quirks")

    @validator("skills", "constraints", "quirks", each_item=True)
    def validate_array_items(cls, v):
        if not isinstance(v, str):
            raise ValueError("Each item must be a string")
        if not v.strip():
            raise ValueError("Empty strings are not allowed")
        return v


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = Field(None, min_length=2, max_length=100)
    skills: Optional[List[str]]
    constraints: Optional[List[str]]
    quirks: Optional[List[str]]


class AgentResponse(AgentBase):
    """Response schema for returning agent data."""
    id: int

    class Config:
        orm_mode = True
