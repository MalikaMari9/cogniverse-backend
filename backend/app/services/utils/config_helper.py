# app/utils/config_helper.py
from sqlalchemy.orm import Session
from app.db.models.config_model import Config

def get_config_value(db: Session, key: str, default=None):
    """
    Fetch a configuration value by key from the database.
    Returns the default if key not found or inactive.
    """
    cfg = (
    db.query(Config)
    .execution_options(populate_existing=True)
    .filter(Config.config_key.ilike(key), Config.status == "active")
    .first()
)


    return cfg.config_value if cfg else default


def get_int_config(db: Session, key: str, default: int) -> int:
    """Fetch a config as int safely."""
    value = get_config_value(db, key)
    print(f"DEBUG CONFIG FETCH → {key}: {value}")
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_bool_config(db: Session, key: str, default: bool) -> bool:
    """Fetch a config as bool safely."""
    value = get_config_value(db, key)
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value) if value is not None else default
