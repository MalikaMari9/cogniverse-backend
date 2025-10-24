from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, date, time, timedelta, timezone
from app.db.models.credit_model import Billing, CreditTransaction, CreditType
from app.services.utils.config_helper import get_int_config, get_config_value

# ──────────────────────────────────────────────────────────────
# 🕒 Check and refresh daily free credits (config + reset time)
# ──────────────────────────────────────────────────────────────
def refresh_daily_free_credits(db: Session, userid: int):
    """
    Refresh user's daily free credits if last reset occurred before today's cutoff.
    Uses:
      - dailyFreeCredits (int)
      - creditResetTimeUTC (HH:MM, UTC time when reset becomes available)
    """
    billing = db.query(Billing).filter(
        Billing.userid == userid,
        Billing.is_deleted == False
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    # ────────────────────────────────
    # 1️⃣ Get config values
    # ────────────────────────────────
    daily_amount = get_int_config(db, "dailyFreeCredits", default=5)
    reset_time_str = get_config_value(db, "creditResetTimeUTC", default="00:00")

    # Parse "HH:MM" into a UTC time object
    try:
        reset_hour, reset_minute = map(int, reset_time_str.split(":"))
        reset_time_utc = time(reset_hour, reset_minute, tzinfo=timezone.utc)
    except Exception:
        reset_time_utc = time(0, 0, tzinfo=timezone.utc)

    # ────────────────────────────────
    # 2️⃣ Determine if reset should happen
    # ────────────────────────────────
    now_utc = datetime.now(timezone.utc)
    today_reset_dt = datetime.combine(now_utc.date(), reset_time_utc)

    # If now is before today’s reset time, then "effective day" is yesterday
    # so users who already received today’s credits won't reset again until the next window.
    effective_date = today_reset_dt.date()
    if now_utc < today_reset_dt:
        effective_date -= timedelta(days=1)

    refreshed = False
    if billing.last_free_credit_date is None or billing.last_free_credit_date < effective_date:
        billing.free_credits = daily_amount
        billing.last_free_credit_date = effective_date
        db.commit()
        db.refresh(billing)
        refreshed = True

    return {
        "userid": userid,
        "paid_credits": billing.paid_credits,
        "free_credits": billing.free_credits,
        "total_credits": billing.paid_credits + billing.free_credits,
        "refreshed": refreshed,
        "daily_limit": daily_amount,
        "reset_time_utc": reset_time_str,
        "last_free_credit_date": billing.last_free_credit_date,
    }

# ──────────────────────────────────────────────────────────────
# Apply a transaction to a user's billing balance
# (Used for adding or deducting credits)
# ──────────────────────────────────────────────────────────────
def apply_credit_transaction(db: Session, transaction_id: int):
    tx = db.query(CreditTransaction).filter(
        CreditTransaction.transactionid == transaction_id,
        CreditTransaction.is_deleted == False
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    billing = db.query(Billing).filter(
        Billing.userid == tx.userid,
        Billing.is_deleted == False
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    # ─────────────────────────────
    # Perform balance updates
    # ─────────────────────────────
    if tx.credit_type == CreditType.paid:
        billing.paid_credits += tx.amount

    elif tx.credit_type == CreditType.free:
        billing.free_credits += tx.amount

    elif tx.credit_type == CreditType.used:
        remaining = tx.amount
        # deduct from paid first, then free
        if billing.paid_credits >= remaining:
            billing.paid_credits -= remaining
        else:
            remaining -= billing.paid_credits
            billing.paid_credits = 0
            billing.free_credits = max(0, billing.free_credits - remaining)

    # ─────────────────────────────
    # Commit changes and mark transaction as applied
    # ─────────────────────────────
    tx.status = "success"
    db.commit()
    db.refresh(billing)
    db.refresh(tx)

    return {
        "message": f"Transaction {tx.transactionid} applied successfully.",
        "userid": tx.userid,
        "paid_credits": billing.paid_credits,
        "free_credits": billing.free_credits,
        "total_credits": billing.paid_credits + billing.free_credits,
    }


# ──────────────────────────────────────────────────────────────
# Rollback / reverse a transaction (admin only)
# ──────────────────────────────────────────────────────────────
def reverse_credit_transaction(db: Session, transaction_id: int):
    tx = db.query(CreditTransaction).filter(
        CreditTransaction.transactionid == transaction_id,
        CreditTransaction.is_deleted == False
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    billing = db.query(Billing).filter(
        Billing.userid == tx.userid,
        Billing.is_deleted == False
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    # Reverse logic — undo previous effect
    if tx.credit_type == CreditType.paid:
        billing.paid_credits = max(0, billing.paid_credits - tx.amount)

    elif tx.credit_type == CreditType.free:
        billing.free_credits = max(0, billing.free_credits - tx.amount)

    elif tx.credit_type == CreditType.used:
        billing.paid_credits += tx.amount  # refund credits (simple rollback)

    tx.status = "reversed"
    db.commit()
    db.refresh(billing)
    db.refresh(tx)

    return {
        "message": f"Transaction {tx.transactionid} reversed successfully.",
        "userid": tx.userid,
        "paid_credits": billing.paid_credits,
        "free_credits": billing.free_credits,
        "total_credits": billing.paid_credits + billing.free_credits,
    }
