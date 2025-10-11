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

    agentRelationID = Column(Integer, primary_key=True, index=True)
    projectID = Column(Integer, ForeignKey("project_tbl.projectID", ondelete="CASCADE"), nullable=False)
    agentA_ID = Column(Integer, ForeignKey("agent_tbl.agentID", ondelete="CASCADE"), nullable=False)
    agentB_ID = Column(Integer, ForeignKey("agent_tbl.agentID", ondelete="CASCADE"), nullable=False)
    relationAtoB = Column(Integer)
    relationBtoA = Column(Integer)
    return_state = Column(Boolean, default=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        CheckConstraint("agentA_ID <> agentB_ID", name="check_distinct_agents"),
        CheckConstraint("relationAtoB BETWEEN -100 AND 100"),
        CheckConstraint("relationBtoA BETWEEN -100 AND 100"),
        Index("uq_project_agentpair", "projectID", "agentA_ID", "agentB_ID", unique=True),
    )
