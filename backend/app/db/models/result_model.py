from sqlalchemy import Column, Integer, Float, Text, TIMESTAMP, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class ResultType(str, enum.Enum):
    system = "system"       # main simulation narration log
    emotion = "emotion"     # emotional state timeline
    memory = "memory"       # memory log or recall
    corrosion = "corrosion" # corroded memory or dark influence
    summary = "summary"     # final summary or synthesis
    position = "position" 

class Result(Base):
    __tablename__ = "result_tbl"

    resultid = Column(Integer, primary_key=True, index=True)
    projectagentid = Column(Integer, ForeignKey("projectagent_tbl.projagentid", ondelete="CASCADE"), nullable=True)
    scenarioid = Column(Integer, ForeignKey("scenario_tbl.scenarioid", ondelete="CASCADE"), nullable=False)
    resulttype = Column(Enum(ResultType, name="result_type"))

    sequence_no = Column(Integer)
    confidence_score = Column(Float)
    resulttext = Column(Text)
    status = Column(Enum(LifecycleStatus, name="lifecycle_status"), default=LifecycleStatus.active)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)