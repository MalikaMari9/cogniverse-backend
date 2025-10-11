from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Enum, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ProjectAgent(Base):
    __tablename__ = "projectagent_tbl"

    projagentid = Column(Integer, primary_key=True, index=True)
    projectid = Column(Integer, ForeignKey("project_tbl.projectid", ondelete="CASCADE"), nullable=False)
    agentid = Column(Integer, ForeignKey("agent_tbl.agentid", ondelete="CASCADE"), nullable=False)
    agentsnapshot = Column(JSON)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (UniqueConstraint("projectid", "agentid", name="uq_project_agent"),)