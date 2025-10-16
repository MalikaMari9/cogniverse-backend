from sqlalchemy import Column, Integer, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# -------------------------------------------
# Enum for lifecycle_status
# -------------------------------------------
class LifecycleStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"


# -------------------------------------------
# Weaver Model
# -------------------------------------------
class Weaver(Base):
    __tablename__ = "weaver_tbl"

    weaverid = Column(Integer, primary_key=True, index=True)
    weavercontent = Column(Text, nullable=False)

    agentid = Column(Integer, ForeignKey("agent_tbl.agentid", ondelete="CASCADE"), nullable=False)
    projectid = Column(Integer, ForeignKey("project_tbl.projectid", ondelete="CASCADE"), nullable=False)

    status = Column(Enum(LifecycleStatus), default=LifecycleStatus.active)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)

    # Relationships
    agent = relationship("Agent", backref="weavers")
    project = relationship("Project", backref="weavers")

    def __repr__(self):
        return f"<Weaver(weaverid={self.weaverid}, agentid={self.agentid}, projectid={self.projectid})>"
