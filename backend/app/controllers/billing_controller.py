from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from app.db.models.credit_model import Billing, LifecycleStatus
from app.db.schemas.billing_schema import BillingCreate, BillingUpdate

# ──────────────────────────────────────────────────────────────
# 1️⃣ Create a billing record for new user
# ──────────────────────────────────────────────────────────────
# app/controllers/billing_controller.py
from datetime import datetime, timezone
from app.db.models.credit_model import Billing
from fastapi import HTTPException, status

def create_billing_record(db: Session, billing_data: BillingCreate):
    existing = db.query(Billing).filter(Billing.userid == billing_data.userid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Billing already exists for this user")

    new_billing = Billing(
        userid=billing_data.userid,
        paid_credits=billing_data.paid_credits or 0,
        free_credits=billing_data.free_credits or 5,
        last_free_credit_date=datetime.now(timezone.utc).date(),  # ✅ set date here
        status="active",
    )

    db.add(new_billing)
    db.commit()
    db.refresh(new_billing)
    return new_billing


# ──────────────────────────────────────────────────────────────
# 2️⃣ Get all billings (Admin only)
# ──────────────────────────────────────────────────────────────
def get_all_billings(db: Session):
    billings = db.query(Billing).filter(Billing.is_deleted == False).all()
    for b in billings:
        b.total_credits = b.paid_credits + b.free_credits
    return billings


# ──────────────────────────────────────────────────────────────
# 3️⃣ Get billing by user ID (auto-refresh daily free credits)
# ──────────────────────────────────────────────────────────────
def get_billing_by_userid(db: Session, userid: int):
    billing = db.query(Billing).filter(
        Billing.userid == userid,
        Billing.is_deleted == False
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    today = date.today()
    if billing.last_free_credit_date != today:
        billing.free_credits = 5
        billing.last_free_credit_date = today
        db.commit()
        db.refresh(billing)

    billing.total_credits = billing.paid_credits + billing.free_credits
    return billing


# ──────────────────────────────────────────────────────────────
# 4️⃣ Update billing (Admin only)
# ──────────────────────────────────────────────────────────────
def update_billing(db: Session, billing_id: int, update_data: BillingUpdate):
    billing = db.query(Billing).filter(Billing.billingid == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(billing, key, value)

    db.commit()
    db.refresh(billing)
    billing.total_credits = billing.paid_credits + billing.free_credits
    return billing


# ──────────────────────────────────────────────────────────────
# 5️⃣ Soft delete billing
# ──────────────────────────────────────────────────────────────
def delete_billing(db: Session, billing_id: int):
    billing = db.query(Billing).filter(Billing.billingid == billing_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    billing.is_deleted = True
    db.commit()
    return {"message": f"Billing {billing_id} marked as deleted."}
