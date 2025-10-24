from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    Enum,
    Numeric,
    Date,
    JSON,
)
from sqlalchemy.sql import func
from app.db.models.user_model import Base
import enum


# ------------------------------------------------------------
# Shared Enum
# ------------------------------------------------------------
class LifecycleStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class CreditType(str, enum.Enum):
    paid = "paid"
    free = "free"
    used = "used"


# ------------------------------------------------------------
# 1. credit_config_tbl — Credit Pack Configurations
# ------------------------------------------------------------
class CreditConfig(Base):
    __tablename__ = "credit_config_tbl"

    creditid = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(50), nullable=False, unique=True)   # e.g. 'pro'
    config_value = Column(JSON, nullable=False)                    # JSON structure for pack
    description = Column(Text)
    status = Column(
    Enum(LifecycleStatus, name="lifecycle_status", create_type=False),
    default=LifecycleStatus.active
)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# ------------------------------------------------------------
# 2. credit_transaction_tbl — Credit Ledger / Stripe Records
# ------------------------------------------------------------
class CreditTransaction(Base):
    __tablename__ = "credit_transaction_tbl"

    transactionid = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)                       # credits quantity
    credit_type = Column(Enum(CreditType), default=CreditType.paid)
    reason = Column(String(100))
    packid = Column(String(50), ForeignKey("credit_config_tbl.config_key", ondelete="SET NULL"))
    amount_paid_usd = Column(Numeric(10, 2))
    stripe_session_id = Column(String(120))
    stripe_payment_intent_id = Column(String(100))
    status = Column(String(20), default="pending")
    remarks = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


# ------------------------------------------------------------
# 3. billing_tbl — User Wallet (Free + Paid Credits)
# ------------------------------------------------------------
class Billing(Base):
    __tablename__ = "billing_tbl"

    billingid = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("user_tbl.userid", ondelete="CASCADE"), nullable=False)
    paid_credits = Column(Integer, nullable=False, default=0)
    free_credits = Column(Integer, nullable=False, default=5)
    last_free_credit_date = Column(Date)
    status = status = Column(
    Enum(LifecycleStatus, name="lifecycle_status", create_type=False),
    default=LifecycleStatus.active
)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
