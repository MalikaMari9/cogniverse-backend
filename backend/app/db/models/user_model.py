#app.db.model.user_model.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

# Enum for user_status
class UserStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"

class User(Base):
    __tablename__ = "user_tbl"

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    profile_image_url = Column(Text)
    stripe_customer_id = Column(String(100))
    status = Column(Enum(UserStatus), default=UserStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return f"<User(userid={self.userid}, email='{self.email}', role='{self.role}')>"
