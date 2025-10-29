# ===============================
# config_validator.py — Config Input Validation
# ===============================
import re
from fastapi import HTTPException

def validate_config_key_value(key: str, value: str | None):
    """
    Validates a config key-value pair before saving to database.
    Raises HTTPException(400) if the value doesn't meet rules.
    """
    if value is None:
        return True

    key_lower = key.lower()
    val_str = str(value).strip()

    # Pagination / Limits
    if "paginationlimit" in key_lower:
        if not val_str.isdigit() or int(val_str) <= 0 or int(val_str) > 100:
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be a positive integer (1–100)."
            )

    # Timeout / Expiry durations
    elif any(w in key_lower for w in ["timeout", "expiry", "duration"]):
        if not val_str.isdigit() or int(val_str) <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be a positive integer."
            )

    # Daily credits and similar numeric configs
    elif "credit" in key_lower and "time" not in key_lower:
        if not val_str.isdigit() or int(val_str) < 0:
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be a non-negative integer."
            )

    # Time (HH:MM) format
    elif "timeutc" in key_lower:
        if not re.match(r"^\d{2}:\d{2}$", val_str):
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be in HH:MM (UTC) format."
            )

    # Email fields (excluding passwords)
    elif "email" in key_lower and "password" not in key_lower:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", val_str):
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be a valid email address."
            )

    # Port numbers
    elif "port" in key_lower:
        if not val_str.isdigit() or not (1 <= int(val_str) <= 65535):
            raise HTTPException(
                status_code=400,
                detail=f"{key} must be a valid port number (1–65535)."
            )

    # No specific rule → accepted
    return True
