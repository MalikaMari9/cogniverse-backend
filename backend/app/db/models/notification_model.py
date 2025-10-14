from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db.models.user_model import Base

class Notification(Base):
    __tablename__ = "notification_tbl"

    notificationid = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String(50))
    related_entity_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
