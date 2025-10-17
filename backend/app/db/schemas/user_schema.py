from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ---------- Base ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr

# ---------- Create ----------
class UserCreate(UserBase):
    password: str

# ---------- Update ----------
class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    profile_image_url: Optional[str]

# ---------- Response ----------
class UserResponse(UserBase):
    userid: int
    role: str
    profile_image_url: Optional[str] = None  # base64 string
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 syntax

# ---------- Login ----------
class UserLogin(BaseModel):
    identifier: str   # can be email or username
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str

# ---------- Generic Message ----------
class MessageResponse(BaseModel):
    message: str
