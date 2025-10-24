# app/db/models/project_model.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.models.user_model import Base

class ProjectStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"

class Project(Base):
    __tablename__ = "project_tbl"

    projectid = Column(Integer, primary_key=True, index=True)
    projectname = Column(String(100), nullable=False)
    project_desc = Column(Text)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.draft)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)
    
    user = relationship("User", backref="projects")