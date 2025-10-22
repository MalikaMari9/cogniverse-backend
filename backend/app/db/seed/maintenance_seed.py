from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.maintenance_model import Maintenance


def seed_maintenance(db: Session):
    """Insert default maintenance modules if they don't already exist."""

    defaults = [
        {
            "module_key": "Global",
            "under_maintenance": False,
            "message": "System-wide maintenance mode",
            "updated_by": 6,
        },
        {
            "module_key": "Project",
            "under_maintenance": False,
            "message": "Project system is currently locked for updates",
            "updated_by": 6,
        },
        {
            "module_key": "WorkStation",
            "under_maintenance": False,
            "message": "Workstation environment temporarily unavailable",
            "updated_by": 6,
        },
        {
            "module_key": "Billing",
            "under_maintenance": False,
            "message": "Billing and credit services are under maintenance",
            "updated_by": None,
        },
        {
            "module_key": "Noti",
            "under_maintenance": False,
            "message": "Notification service temporarily disabled",
            "updated_by": 6,
        },
    ]

    added = 0
    for entry in defaults:
        existing = db.query(Maintenance).filter(Maintenance.module_key == entry["module_key"]).first()
        if not existing:
            entry["created_at"] = datetime.utcnow()
            entry["updated_at"] = datetime.utcnow()
            db.add(Maintenance(**entry))
            added += 1

    try:
        db.commit()
        print(f"✅ Maintenance seeding complete. {added} new module(s) added.")
    except Exception as e:
        db.rollback()
        print(f"❌ Maintenance seeding failed: {e}")
