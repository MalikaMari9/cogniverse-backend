from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.models.user_model import Base

class RevokedToken(Base):
    __tablename__ = "revoked_token_tbl"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user_tbl.userid"))
    revoked_at = Column(TIMESTAMP, server_default=func.now())
