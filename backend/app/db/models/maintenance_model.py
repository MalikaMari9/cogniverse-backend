from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.models.user_model import Base

class Maintenance(Base):
    __tablename__ = "maintenance_tbl"

    maintenanceid = Column(Integer, primary_key=True, index=True)
    module_key = Column(String(100), unique=True, nullable=False)
    under_maintenance = Column(Boolean, default=False, nullable=False)

    message = Column(Text)
    updated_by = Column(Integer, ForeignKey("user_tbl.userid"))
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    updater = relationship("User", backref="maintenances", lazy="joined")
    deleted_at = Column(TIMESTAMP)