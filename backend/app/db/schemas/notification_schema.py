from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    userid: int
    title: str = Field(..., max_length=150)
    message: str
    is_read: Optional[bool] = False
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    message: Optional[str] = None
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    notificationid: int
    created_at: datetime

    class Config:
        from_attributes = True
