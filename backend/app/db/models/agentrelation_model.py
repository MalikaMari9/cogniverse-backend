from sqlalchemy import Column, Integer, ForeignKey, Boolean, TIMESTAMP, Enum, CheckConstraint, Index
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class AgentRelation(Base):
    __tablename__ = "agentrelation_tbl"

    agentrelationid = Column(Integer, primary_key=True, index=True)
    projectid = Column(Integer, ForeignKey("project_tbl.projectid", ondelete="CASCADE"), nullable=False)
    agenta_id = Column(Integer, ForeignKey("agent_tbl.agentid", ondelete="CASCADE"), nullable=False)
    agentb_id = Column(Integer, ForeignKey("agent_tbl.agentid", ondelete="CASCADE"), nullable=False)
    relationatob = Column(Integer)
    relationbtoa = Column(Integer)
    return_state = Column(Boolean, default=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint("agenta_id <> agentb_id", name="check_distinct_agents"),
        CheckConstraint("relationatob BETWEEN -100 AND 100"),
        CheckConstraint("relationbtoa BETWEEN -100 AND 100"),
        Index("uq_project_agentpair", "projectid", "agenta_id", "agentb_id", unique=True),
    )