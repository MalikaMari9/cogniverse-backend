from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaintenanceBase(BaseModel):
    module_key: str
    under_maintenance: bool
    message: Optional[str] = None

class MaintenanceUpdate(BaseModel):
    under_maintenance: Optional[bool] = None
    message: Optional[str] = None

class MaintenanceResponse(MaintenanceBase):
    maintenanceid: int
    updated_by: Optional[int] = None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
