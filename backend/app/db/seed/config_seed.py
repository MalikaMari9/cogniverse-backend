from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.config_model import Config


def seed_configs(db: Session):
    """Insert default system configuration values if they don't already exist."""

    defaults = [
        {
            "config_key": "TestConfig",
            "config_value": "Test",
            "description": "Test",
            "status": "active",
        },
        {
            "config_key": "accessTokenExpiryMinutes",
            "config_value": "30",
            "description": "Access token lifetime in minutes",
            "status": "active",
        },
        {
            "config_key": "refreshTokenExpiryDays",
            "config_value": "7",
            "description": "Refresh token lifetime in days",
            "status": "active",
        },
        {
            "config_key": "ProjectPaginationLimit",
            "config_value": "8",
            "description": "Default number of projects per page",
            "status": "active",
        },
        {
            "config_key": "AgentPaginationLimit",
            "config_value": "8",
            "description": "Default number of agents per page",
            "status": "active",
        },
        {
            "config_key": "LogPaginationLimit",
            "config_value": "50",
            "description": "Number of log entries per page in admin dashboard",
            "status": "active",
        },
        {
            "config_key": "supportEmail",
            "config_value": "support@cogniverse.ai",
            "description": "Support contact email address",
            "status": "active",
        },
        {
            "config_key": "supportPhone",
            "config_value": "+959123456789",
            "description": "Support contact phone number",
            "status": "active",
        },
        {
            "config_key": "companyName",
            "config_value": "CogniVerse Systems",
            "description": "Displayed company name",
            "status": "active",
        },
        {
            "config_key": "dailyFreeCredits",
            "config_value": "5",
            "description": "Number of free credits given to users daily",
            "status": "active",
        },
        {
            "config_key": "creditResetTimeUTC",
            "config_value": "00:00",
            "description": "Time (UTC) when free credits reset globally",
            "status": "active",
        },
        {
            "config_key": "smtpSenderEmail",
            "config_value": "no-reply@cogniverse.ai",
            "description": "Default sender address for system emails",
            "status": "active",
        },
        {
            "config_key": "simulationTimeoutSeconds",
            "config_value": "120",
            "description": "Maximum simulation runtime per request (in seconds)",
            "status": "active",
        },
    ]

    added = 0
    for entry in defaults:
        existing = db.query(Config).filter(Config.config_key == entry["config_key"]).first()
        if not existing:
            entry["created_at"] = datetime.utcnow()
            entry["updated_at"] = datetime.utcnow()
            db.add(Config(**entry))
            added += 1

    try:
        db.commit()
        print(f"✅ Config seeding complete. {added} new configuration(s) added.")
    except Exception as e:
        db.rollback()
        print(f"❌ Config seeding failed: {e}")
