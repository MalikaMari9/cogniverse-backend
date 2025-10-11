from sqlalchemy import Column, Integer, Float, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ResultType(str, enum.Enum):
    text = "text"
    summary = "summary"
    log = "log"

class Result(Base):
    __tablename__ = "result_tbl"

    resultid = Column(Integer, primary_key=True, index=True)
    projectagentid = Column(Integer, ForeignKey("projectagent_tbl.projagentid", ondelete="CASCADE"), nullable=False)
    scenarioid = Column(Integer, ForeignKey("scenario_tbl.scenarioid", ondelete="CASCADE"), nullable=False)
    resulttype = Column(Enum(ResultType))
    sequence_no = Column(Integer)
    confidence_score = Column(Float)
    resulttext = Column(Text)
    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)