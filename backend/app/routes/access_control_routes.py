# ===============================
# app/routes/access_control_routes.py — With Universal Logging
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.schemas.access_control_schema import (
    AccessControlCreate,
    AccessControlUpdate,
    AccessControlResponse,
)
from app.controllers import access_control_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/access-controls", tags=["Access Controls"])


# ============================================================
# 🔹 GET ALL ACCESS CONTROLS (requires READ access)
# ============================================================
@router.get("/", response_model=List[AccessControlResponse])
async def get_all_access_controls(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
        result = access_control_controller.get_all_access_controls(db)

        await log_action(
            db, request, current_user,
            "ACCESS_CONTROL_LIST_VIEW",
            details="Viewed all access controls"
        )

        return result

    except Exception as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_LIST_ERROR", e, "Error viewing access controls")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET SINGLE ACCESS CONTROL (requires READ access)
# ============================================================
@router.get("/{access_id}", response_model=AccessControlResponse)
async def get_access_control(
    access_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
        access = access_control_controller.get_access_by_id(access_id, db)

        await log_action(
            db, request, current_user,
            "ACCESS_CONTROL_VIEW",
            details=f"Viewed access control ID: {access_id}",
            dedupe_key=f"access_{access_id}"
        )

        return access

    except HTTPException as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_VIEW_FAILED", e, f"Failed to view access control {access_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_VIEW_ERROR", e, f"Error viewing access control {access_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 CREATE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.post("/", response_model=AccessControlResponse, status_code=201)
async def create_access_control(
    access: AccessControlCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
        result = access_control_controller.create_access_control(access, db)

        await log_action(
            db, request, current_user,
            "ACCESS_CONTROL_CREATE",
            details=f"Created access control for module '{access.module_key}'"

        )

        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_CREATE_FAILED", e, "Failed to create access control")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_CREATE_ERROR", e, "Error creating access control")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.put("/{access_id}", response_model=AccessControlResponse)
async def update_access_control(
    access_id: int,
    access: AccessControlUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)

        old_data = access_control_controller.get_access_by_id(access_id, db)
        if not old_data:
            raise HTTPException(status_code=404, detail=f"Access control {access_id} not found")

        result = access_control_controller.update_access_control(access_id, access, db)


        await log_action(
            db, request, current_user,
            "ACCESS_CONTROL_UPDATE",
            details=f"Updated access control ID {access_id} "
                    f"({old_data.module_key}) — levels updated."
        )

        return result

    except Exception as e:
        import traceback
        print("🚨 [AccessControl Update Error]", traceback.format_exc())
        await log_error(db, request, current_user, "ACCESS_CONTROL_UPDATE_ERROR", e, f"Error updating access control {access_id}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 🔹 DELETE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.delete("/{access_id}")
async def delete_access_control(
    access_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
        access_control_controller.delete_access_control(access_id, db)

        await log_action(
            db, request, current_user,
            "ACCESS_CONTROL_DELETE",
            details=f"Deleted access control ID {access_id}"
        )

        return {"message": f"Access control {access_id} deleted successfully"}

    except Exception as e:
        await log_error(db, request, current_user, "ACCESS_CONTROL_DELETE_ERROR", e, f"Error deleting access control {access_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
