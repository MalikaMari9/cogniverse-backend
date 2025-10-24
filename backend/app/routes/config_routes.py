# ===============================
# app/routes/config_routes.py — With Universal Logging
# ===============================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.config_schema import ConfigCreate, ConfigUpdate, ConfigResponse
from app.controllers import config_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user
from app.services.route_logger_helper import log_action, log_error

router = APIRouter(prefix="/configs", tags=["Configs"])


# ============================================================
# 🔹 GET ALL CONFIGS (requires READ access)
# ============================================================
@router.get("/", response_model=List[ConfigResponse])
async def get_all_configs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CONFIGURATION", request)
        result = config_controller.get_all_configs(db)

        await log_action(
            db, request, current_user,
            "CONFIG_LIST_VIEW",
            details="Viewed all system configurations"
        )
        return result

    except Exception as e:
        await log_error(db, request, current_user, "CONFIG_LIST_ERROR", e, "Error viewing all configs")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 GET SINGLE CONFIG (requires READ access)
# ============================================================
@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CONFIGURATION", request)
        config = config_controller.get_config_by_id(config_id, db)

        await log_action(
            db, request, current_user,
            "CONFIG_VIEW",
            details=f"Viewed configuration ID: {config_id}",
            dedupe_key=f"config_{config_id}"
        )
        return config

    except HTTPException as e:
        await log_error(db, request, current_user, "CONFIG_VIEW_FAILED", e, f"Failed to view config {config_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CONFIG_VIEW_ERROR", e, f"Error viewing config {config_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 CREATE CONFIG (requires WRITE access)
# ============================================================
@router.post("/", response_model=ConfigResponse, status_code=201)
async def create_config(
    config: ConfigCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CONFIGURATION", request)
        result = config_controller.create_config(config, db)

        await log_action(
            db, request, current_user,
            "CONFIG_CREATE",
            details=f"Created config '{config.config_key}' = '{config.config_value}'"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "CONFIG_CREATE_FAILED", e, "Failed to create config")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CONFIG_CREATE_ERROR", e, "Error creating config")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 UPDATE CONFIG (requires WRITE access)
# ============================================================
@router.put("/{config_id}", response_model=ConfigResponse)
async def update_config(
    config_id: int,
    config: ConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CONFIGURATION", request)
        old_data = config_controller.get_config_by_id(config_id, db)
        result = config_controller.update_config(config_id, config, db)

        await log_action(
            db, request, current_user,
            "CONFIG_UPDATE",
            details=f"Updated config ID {config_id} ({old_data.config_key}): '{old_data.config_value}' → '{config.config_value}'"
        )
        return result

    except HTTPException as e:
        await log_error(db, request, current_user, "CONFIG_UPDATE_FAILED", e, f"Failed to update config {config_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CONFIG_UPDATE_ERROR", e, f"Error updating config {config_id}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 DELETE CONFIG (requires WRITE access)
# ============================================================
@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "CONFIGURATION", request)
        config_controller.delete_config(config_id, db)

        await log_action(
            db, request, current_user,
            "CONFIG_DELETE",
            details=f"Deleted configuration ID {config_id}"
        )
        return {"message": f"Configuration {config_id} deleted successfully"}

    except HTTPException as e:
        await log_error(db, request, current_user, "CONFIG_DELETE_FAILED", e, f"Failed to delete config {config_id}")
        raise e
    except Exception as e:
        await log_error(db, request, current_user, "CONFIG_DELETE_ERROR", e, f"Error deleting config {config_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
