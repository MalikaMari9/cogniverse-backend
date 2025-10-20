# app/routes/permissions_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.utils.permissions_helper import get_access_level_for_user
from app.services.jwt_service import get_current_user
from app.db.database import get_db

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("/{module_key}")
def get_user_module_permission(
    module_key: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns the current user's access level for a given module.
    Example response: {"module_key": "PROJECTS", "access_level": "write"}
    """
    level = get_access_level_for_user(db, current_user, module_key)
    return {"module_key": module_key, "access_level": level}
