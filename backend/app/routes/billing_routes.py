from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.schemas.billing_schema import (
    BillingCreate, BillingUpdate, BillingResponse
)
from app.controllers import billing_controller
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto

router = APIRouter(prefix="/billing", tags=["Billing"])

# ──────────────────────────────────────────────────────────────
# 🟢 Create billing (Admin only)
# ──────────────────────────────────────────────────────────────
@router.post("/", response_model=BillingResponse)
def create_billing(
    billing: BillingCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)
    return billing_controller.create_billing_record(db, billing)


# ──────────────────────────────────────────────────────────────
# 🔵 Get all billings (Admin)
# ──────────────────────────────────────────────────────────────
@router.get("/", response_model=List[BillingResponse])
def get_all_billings(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)
    return billing_controller.get_all_billings(db)

# ──────────────────────────────────────────────────────────────
# 🟢 Get current user billing (auto-refresh via config)
# ──────────────────────────────────────────────────────────────
from app.services.credit_service import refresh_daily_free_credits

@router.get("/me", response_model=BillingResponse)
def get_my_billing(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)

    # 🕒 Step 1: refresh free credits if past reset window
    refresh_result = refresh_daily_free_credits(db, current_user.userid)

    # 🧾 Step 2: get up-to-date wallet info
    wallet = billing_controller.get_billing_by_userid(db, current_user.userid)

    # 🧩 Step 3: merge helpful info for frontend (optional)
    wallet.total_credits = wallet.paid_credits + wallet.free_credits

    # Add optional debug info (not part of schema — returned dynamically)
    return {
        **wallet.__dict__,
        "refreshed": refresh_result["refreshed"],
        "daily_limit": refresh_result["daily_limit"],
        "reset_time_utc": refresh_result["reset_time_utc"],
    }

# ──────────────────────────────────────────────────────────────
# 🟠 Get billing by user ID (Admin)
# ──────────────────────────────────────────────────────────────
@router.get("/{userid}", response_model=BillingResponse)
def get_billing_for_user(
    userid: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)
    return billing_controller.get_billing_by_userid(db, userid)


# ──────────────────────────────────────────────────────────────
# 🟣 Update billing (Admin)
# ──────────────────────────────────────────────────────────────
@router.put("/{billing_id}", response_model=BillingResponse)
def update_billing(
    billing_id: int,
    billing: BillingUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)
    return billing_controller.update_billing(db, billing_id, billing)


# ──────────────────────────────────────────────────────────────
# 🔴 Soft delete billing (Admin)
# ──────────────────────────────────────────────────────────────
@router.delete("/{billing_id}")
def delete_billing(
    billing_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enforce_permission_auto(db, current_user, "BILLING", request)
    return billing_controller.delete_billing(db, billing_id)
