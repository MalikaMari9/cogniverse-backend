from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum, ARRAY
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class Agent(Base):
    __tablename__ = "agent_tbl"

    agentID = Column(Integer, primary_key=True, index=True)
    agentName = Column(String(100), nullable=False)
    agentPersonality = Column(String(20))
    agentSkill = Column(ARRAY(String(50)), default=[])
    agentBiography = Column(Text)
    agentConstraints = Column(ARRAY(String(50)), default=[])
    agentQuirk = Column(ARRAY(String(50)), default=[])
    agentMotivation = Column(Text)
    userID = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
