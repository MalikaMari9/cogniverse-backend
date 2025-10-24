from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class SystemLog(Base):
    __tablename__ = "system_log_tbl"

    logid = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(100), nullable=False)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="SET NULL"))
    details = Column(Text)
    ip_address = Column(String(45))
    browser_info = Column(String(200))
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP)
    # Add relationship to User
    user = relationship("User", backref="system_logs", lazy="joined")