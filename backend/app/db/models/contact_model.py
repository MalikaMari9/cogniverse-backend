from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum


class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class Contact(Base):
    __tablename__ = "contact_tbl"

    contactid = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="SET NULL"))
    email = Column(String(100), nullable=False)
    subject = Column(String(150))
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
