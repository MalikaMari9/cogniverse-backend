from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Enum
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum

class LifecycleStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"

class AccessLevel(str, enum.Enum):
    none = "none"
    read = "read"
    write = "write"

class AccessControl(Base):
    __tablename__ = "access_control_tbl"

    accessid = Column(Integer, primary_key=True, index=True)
    module_key = Column(String(100), unique=True, nullable=False)
    module_desc = Column(Text)

    # 🧠 FIX: explicitly link to Postgres enum type name
    user_access = Column(Enum(AccessLevel, name="access_level_enum", create_type=False), default=AccessLevel.none)
    admin_access = Column(Enum(AccessLevel, name="access_level_enum", create_type=False), default=AccessLevel.none)
    superadmin_access = Column(Enum(AccessLevel, name="access_level_enum", create_type=False), default=AccessLevel.none)
    is_critical = Column(Boolean, default=False)
    status = Column(Enum(LifecycleStatus, name="lifecycle_status", create_type=False), default=LifecycleStatus.active)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
