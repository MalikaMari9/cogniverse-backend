from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"

# ---------- Base ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr

# ---------- Create ----------
class UserCreate(UserBase):
    password: str
    role: str = "user"

# ---------- Update ----------
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    profile_image_url: Optional[str] = None

# ---------- Admin Update ----------
class UserAdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[UserStatus] = None
    profile_image_url: Optional[str] = None

# ---------- Response ----------
class UserResponse(UserBase):
    userid: int
    role: str
    profile_image_url: Optional[str] = None
    status: str
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------- List Response ----------
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int

# ---------- Login ----------
class UserLogin(BaseModel):
    identifier: str   # can be email or username
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str

# ---------- Password Change ----------
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordChangeResponse(BaseModel):
    message: str

# ---------- Status Change ----------
class UserStatusUpdate(BaseModel):
    status: UserStatus

class UserStatusResponse(BaseModel):
    message: str
    user_id: int
    new_status: str

# ---------- Generic Message ----------
class MessageResponse(BaseModel):
    message: str

# ---------- Bulk Operations ----------
class BulkUserOperation(BaseModel):
    user_ids: List[int]

class BulkOperationResponse(BaseModel):
    message: str
    processed: int
    failed: int