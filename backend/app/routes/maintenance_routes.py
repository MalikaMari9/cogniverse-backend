# backend/app/routes/maintenance_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from app.db.database import get_db
from app.db.schemas.maintenance_schema import MaintenanceResponse, MaintenanceUpdate
from app.controllers import maintenance_controller as controller
from app.services.jwt_service import get_current_user
from app.db.models.maintenance_model import Maintenance
from app.services.utils.permissions_helper import enforce_permission_auto

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ===============================
# 🔹 Get global maintenance entry (PUBLIC)
# ===============================
@router.get("/global")
def get_global_maintenance(db: Session = Depends(get_db)):
    global_entry = (
        db.query(Maintenance)
        .filter(func.lower(Maintenance.module_key) == "global")
        .first()
    )
    if not global_entry:
        raise HTTPException(status_code=404, detail="Global maintenance entry not found")
    return {
        "module_key": global_entry.module_key,
        "under_maintenance": global_entry.under_maintenance,
        "message": global_entry.message,
        "updated_at": global_entry.updated_at,
    }


# ===============================
# 🔹 Get all maintenance modules
# ===============================
@router.get("/", response_model=List[MaintenanceResponse])
def get_all_maintenance(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "MAINTENANCE", request)
    return controller.get_all_maintenance(db)


@router.get("", include_in_schema=False)
def get_all_maintenance_alias(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_all_maintenance(request, db, current_user)


# ===============================
# 🔹 Update maintenance module
# ===============================
@router.put("/{module_key}", response_model=MaintenanceResponse)
def update_maintenance(
    module_key: str,
    data: MaintenanceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "MAINTENANCE", request)
    return controller.update_maintenance(db, module_key, data, current_user.userid)


# ===============================
# 🔹 Get single module maintenance (public read)
# ===============================
@router.get("/{module_key}")
def get_module_maintenance(
    module_key: str,
    db: Session = Depends(get_db),
    request: Request = None,  # optional, not really used
):
    """
    Anyone (logged in or not) can check maintenance status.
    Only admins can update via PUT.
    """
    entry = (
        db.query(Maintenance)
        .filter(func.lower(Maintenance.module_key) == module_key.lower())
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail=f"No maintenance entry for {module_key}")

    return {
        "module_key": entry.module_key,
        "under_maintenance": entry.under_maintenance,
        "message": entry.message,
        "updated_at": entry.updated_at,
    }
