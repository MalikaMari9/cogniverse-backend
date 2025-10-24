# ===============================
# app/routes/maintenance_routes.py — With Universal Logging
# ===============================

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.db.schemas.maintenance_schema import MaintenanceResponse, MaintenanceUpdate
from app.controllers import maintenance_controller as controller
from app.db.models.maintenance_model import Maintenance
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ============================================================
# 🔹 Get Global Maintenance Entry (PUBLIC)
# ============================================================
@router.get("/global")
async def get_global_maintenance(db: Session = Depends(get_db)):
    try:
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

    except Exception as e:
        print("⚠️ [Global Maintenance Fetch Error]", e)
        raise HTTPException(status_code=500, detail="Failed to fetch global maintenance info")


# ============================================================
# 🔹 Get All Maintenance Modules (Admin)
# ============================================================
@router.get("/", response_model=List[MaintenanceResponse])
async def get_all_maintenance(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "MAINTENANCE", request)
        result = controller.get_all_maintenance(db)

        await log_action(
            db, request, current_user,
            "MAINTENANCE_LIST_VIEW",
            details="Viewed all maintenance module entries"
        )
        return result

    except Exception as e:
        await log_error(db, request, current_user, "MAINTENANCE_LIST_ERROR", e, "Error viewing maintenance list")
        raise HTTPException(status_code=500, detail="Internal server error")


# Alias endpoint (without trailing slash)
@router.get("", include_in_schema=False)
async def get_all_maintenance_alias(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_all_maintenance(request, db, current_user)


# ============================================================
# 🔹 Update Maintenance Module (Admin)
# ============================================================
@router.put("/{module_key}", response_model=MaintenanceResponse)
async def update_maintenance(
    module_key: str,
    data: MaintenanceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "MAINTENANCE", request)
        result = controller.update_maintenance(db, module_key, data, current_user.userid)

        action = "activated" if data.under_maintenance else "deactivated"
        await log_action(
            db, request, current_user,
            "MAINTENANCE_UPDATE",
            details=f"{action.capitalize()} maintenance for module '{module_key}'"
        )

        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "MAINTENANCE_UPDATE_FAILED", e, f"Failed to update maintenance for {module_key}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "MAINTENANCE_UPDATE_ERROR", e, f"Error updating maintenance for {module_key}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Get Single Module Maintenance (PUBLIC)
# ============================================================
@router.get("/{module_key}")
async def get_module_maintenance(
    module_key: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Anyone (logged in or not) can check maintenance status.
    Only admins can update via PUT.
    """
    try:
        entry = (
            db.query(Maintenance)
            .filter(func.lower(Maintenance.module_key) == module_key.lower())
            .first()
        )
        if not entry:
            raise HTTPException(status_code=404, detail=f"No maintenance entry for {module_key}")

        # Optional public view logging (no user)
        await log_action(
            db, request, current_user=None,
            action_type="MAINTENANCE_VIEW_PUBLIC",
            details=f"Publicly viewed maintenance status for module '{module_key}'"
        )

        return {
            "module_key": entry.module_key,
            "under_maintenance": entry.under_maintenance,
            "message": entry.message,
            "updated_at": entry.updated_at,
        }

    except HTTPException as e:
        await log_error(db, request, None, "MAINTENANCE_VIEW_FAILED", e, f"Failed to fetch maintenance for {module_key}")
        raise e
    except Exception as e:
        await log_error(db, request, None, "MAINTENANCE_VIEW_ERROR", e, f"Error fetching maintenance for {module_key}")
        raise HTTPException(status_code=500, detail="Internal server error")
