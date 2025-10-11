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
    projectName: str = Field(..., max_length=100)
    project_desc: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    status: Optional[ProjectStatus] = None

class ProjectResponse(ProjectBase):
    projectID: int
    userID: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
