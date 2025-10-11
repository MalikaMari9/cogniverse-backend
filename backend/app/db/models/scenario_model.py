from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class Scenario(Base):
    __tablename__ = "scenario_tbl"

    scenarioID = Column(Integer, primary_key=True, index=True)
    scenarioName = Column(String(100))
    scenarioPrompt = Column(Text)
    projectID = Column(Integer, ForeignKey("project_tbl.projectID", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
