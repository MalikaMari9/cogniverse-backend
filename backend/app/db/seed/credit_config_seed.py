from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.credit_model import CreditConfig, LifecycleStatus


def seed_credit_packs(db: Session):
    """Insert default credit packs if they don't already exist."""

    packs = [
        {
            "config_key": "starter",
            "config_value": {
                "name": "Starter Pack",
                "credits": 5,
                "base_price_usd": 5,
                "discount_percent": 0,
                "stripe_price_id": "price_starter_123",
                "badge": "New",
                "tone": "cyan"
            },
            "description": "Starter Pack – perfect for quick testing",
            "status": LifecycleStatus.active,
        },
        {
            "config_key": "basic",
            "config_value": {
                "name": "Basic Pack",
                "credits": 10,
                "base_price_usd": 10,
                "discount_percent": 0,
                "stripe_price_id": "price_basic_123",
                "badge": "Popular",
                "tone": "violet"
            },
            "description": "Basic Pack – for light users",
            "status": LifecycleStatus.active,
        },
        {
            "config_key": "standard",
            "config_value": {
                "name": "Standard Pack",
                "credits": 20,
                "base_price_usd": 20,
                "discount_percent": 0,
                "stripe_price_id": "price_standard_123",
                "badge": "Balanced",
                "tone": "pink"
            },
            "description": "Standard Pack – mid-scale runs",
            "status": LifecycleStatus.active,
        },
        {
            "config_key": "plus",
            "config_value": {
                "name": "Plus Pack",
                "credits": 50,
                "base_price_usd": 50,
                "discount_percent": 5,
                "stripe_price_id": "price_plus_123",
                "badge": "New Tier",
                "tone": "teal"
            },
            "description": "Plus Pack – for growing teams",
            "status": LifecycleStatus.active,
        },
        {
            "config_key": "pro",
            "config_value": {
                "name": "Pro Pack",
                "credits": 80,
                "base_price_usd": 80,
                "discount_percent": 10,
                "stripe_price_id": "price_pro_123",
                "badge": "Best Value",
                "tone": "teal"
            },
            "description": "Pro Pack – for larger teams and projects",
            "status": LifecycleStatus.active,
        },
        {
            "config_key": "ultimate",
            "config_value": {
                "name": "Ultimate Pack",
                "credits": 100,
                "base_price_usd": 100,
                "discount_percent": 15,
                "stripe_price_id": "price_ultimate_123",
                "badge": "Max Pack",
                "tone": "gold"
            },
            "description": "Ultimate Pack – enterprise-scale credit plan",
            "status": LifecycleStatus.active,
        },
    ]

    added = 0
    for pack in packs:
        existing = db.query(CreditConfig).filter(CreditConfig.config_key == pack["config_key"]).first()
        if not existing:
            pack["created_at"] = datetime.utcnow()
            pack["updated_at"] = datetime.utcnow()
            db.add(CreditConfig(**pack))
            added += 1

    try:
        db.commit()
        print(f"✅ Credit pack seeding complete. {added} new pack(s) added.")
    except Exception as e:
        db.rollback()
        print(f"❌ Credit pack seeding failed: {e}")
