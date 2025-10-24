# ===============================
# app/services/route_logger_helper.py
# Universal logging helper for routes
# ===============================

from fastapi import Request
from sqlalchemy.orm import Session
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service


async def log_action(
    db: Session,
    request: Request,
    current_user,
    action_type: str,
    details: str = "",
    dedupe_key: str = None,
    status: str = "active",
):
    """
    🔹 Log a user/system action with deduplication support.
    - db: SQLAlchemy Session
    - request: FastAPI Request
    - current_user: user dict or model with userid attribute
    - action_type: short uppercase string (e.g., "USER_VIEW")
    - details: optional description text
    - dedupe_key: optional key to prevent rapid duplicates
    - status: usually "active"
    """
    try:
        user_id = getattr(current_user, "userid", None) or getattr(current_user, "user_id", None)

        if dedupe_service.should_log_action(action_type, user_id, dedupe_key):
            await system_logger.log_action(
                db=db,
                action_type=action_type,
                user_id=user_id,
                details=details,
                request=request,
                status=status,
            )
    except Exception as e:
        print(f"[⚠️ LOGGING ERROR] {action_type}: {e}")


async def log_error(
    db: Session,
    request: Request,
    current_user,
    action_type: str,
    error: Exception,
    context: str = "",
    status: str = "active",
):
    """
    🔹 Log an error safely without breaking the main request flow.
    - action_type should use *_ERROR or *_FAILED suffix.
    """
    try:
        user_id = getattr(current_user, "userid", None) or getattr(current_user, "user_id", None)
        await system_logger.log_action(
            db=db,
            action_type=action_type,
            user_id=user_id,
            details=f"{context}: {str(error)}",
            request=request,
            status=status,
        )
    except Exception as e:
        print(f"[⚠️ LOGGING FAILURE] Unable to log error for {action_type}: {e}")
