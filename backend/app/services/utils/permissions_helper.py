# app/services/utils/permissions_helper.py
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.models.access_control_model import AccessControl
from app.db.models.user_model import User


def get_access_level_for_user(db: Session, user: User, module_key: str) -> str:
    """
    Returns the access level ("none", "read", "write") for the given user and module.
    """
    role = (user.role or "user").lower()

    access = (
        db.query(AccessControl)
        .filter(AccessControl.module_key == module_key)
        .first()
    )

    if not access:
        return "none"

    # Ensure correct enum value extraction
    def enum_val(x):
        return x.value if hasattr(x, "value") else x

    if role == "superadmin":
        return enum_val(access.superadmin_access)
    elif role == "admin":
        return enum_val(access.admin_access)
    else:
        return enum_val(access.user_access)


def require_access(db: Session, user: User, module_key: str, required: str = "read"):
    """
    Raises HTTP 403 if the user lacks the required permission.
    required = "read" or "write"
    """
    current_level = get_access_level_for_user(db, user, module_key)

    if current_level == "none":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied for module '{module_key}'."
        )

    # If 'write' required but user only has 'read'
    if required == "write" and current_level != "write":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Write access denied for module '{module_key}'."
        )

    return True


def enforce_permission_auto(db: Session, user: User, module_key: str, request: Request):
    """
    Automatically determine required access level based on HTTP method.
    GET, HEAD, OPTIONS -> "read"
    POST, PUT, PATCH, DELETE -> "write"
    """
    method = request.method.upper()
    if method in ["GET", "HEAD", "OPTIONS"]:
        required = "read"
    else:
        required = "write"

    require_access(db, user, module_key, required)
