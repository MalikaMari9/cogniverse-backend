from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum, ARRAY, Boolean
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class Agent(Base):
    __tablename__ = "agent_tbl"

    agentid = Column(Integer, primary_key=True, index=True)
    agentname = Column(String(100), nullable=False)
    agentpersonality = Column(String(20))
    agentskill = Column(ARRAY(String(50)), default=[])
    agentbiography = Column(Text)
    agentconstraints = Column(ARRAY(String(50)), default=[])
    agentquirk = Column(ARRAY(String(50)), default=[])
    agentmotivation = Column(Text)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)
