# app/db/schemas/project_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"

class ProjectBase(BaseModel):
    projectname: str = Field(..., max_length=100)
    project_desc: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    projectname: Optional[str] = Field(None, max_length=100)
    project_desc: Optional[str] = None
    status: Optional[ProjectStatus] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    projectid: int
    userid: int
    status: ProjectStatus
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None


    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2