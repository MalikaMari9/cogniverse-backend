from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LifecycleStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class ContactBase(BaseModel):
    userid: Optional[int] = None
    email: Optional[EmailStr] = None  
    subject: Optional[str] = Field(None, max_length=150)
    message: str
    is_resolved: Optional[bool] = False
    status: Optional[LifecycleStatus] = LifecycleStatus.active
    


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    subject: Optional[str] = None
    message: Optional[str] = None
    is_resolved: Optional[bool] = None
    status: Optional[LifecycleStatus] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


class ContactResponse(ContactBase):
    contactid: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
    class Config:
        from_attributes = True
