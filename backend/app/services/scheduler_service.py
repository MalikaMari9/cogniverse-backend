from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.db.models.credit_model import Billing
from app.services.utils.config_helper import get_int_config, get_config_value

scheduler = BackgroundScheduler(timezone="UTC")
# NOT USED YET #
def daily_credit_reset():
    db = SessionLocal()
    try:
        daily_amount = get_int_config(db, "dailyFreeCredits", 5)
        reset_time_str = get_config_value(db, "creditResetTimeUTC", "00:00")

        print(f"[{datetime.now(timezone.utc)}] Running global credit reset → {daily_amount} credits")

        billings = db.query(Billing).filter(Billing.is_deleted == False).all()
        for billing in billings:
            billing.free_credits = daily_amount
            billing.last_free_credit_date = datetime.now(timezone.utc).date()
        db.commit()

        print(f"✅ Refreshed {len(billings)} user wallets.")
    except Exception as e:
        print(f"❌ Credit reset failed: {e}")
    finally:
        db.close()

# Schedule daily job
scheduler.add_job(
    daily_credit_reset,
    trigger="cron",
    hour=0, minute=0,  # default 00:00 UTC
    id="daily_credit_reset",
    replace_existing=True,
)
scheduler.start()
