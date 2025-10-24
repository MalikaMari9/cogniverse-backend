from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class Scenario(Base):
    __tablename__ = "scenario_tbl"

    scenarioid = Column(Integer, primary_key=True, index=True)
    scenarioname = Column(String(100))
    scenarioprompt = Column(Text)
    projectid = Column(Integer, ForeignKey("project_tbl.projectid", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)