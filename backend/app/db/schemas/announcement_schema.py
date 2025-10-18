from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class AnnouncementBase(BaseModel):
    title: str = Field(..., max_length=150)
    content: str
    created_by: Optional[int] = None
    status: Optional[LifecycleStatus] = LifecycleStatus.active

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    content: Optional[str] = None
    status: Optional[LifecycleStatus] = None

class AnnouncementResponse(AnnouncementBase):
    announcementid: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_username: Optional[str] = None  # Add this field

    class Config:
        from_attributes = True