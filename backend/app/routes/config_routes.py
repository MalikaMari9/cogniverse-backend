from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.config_schema import ConfigCreate, ConfigUpdate, ConfigResponse
from app.controllers import config_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user

router = APIRouter(prefix="/configs", tags=["Configs"])

# ============================================================
# 🔹 GET ALL CONFIGS (requires READ access)
# ============================================================
@router.get("/", response_model=List[ConfigResponse])
def get_all_configs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "CONFIGURATION", request)
    return config_controller.get_all_configs(db)

# ============================================================
# 🔹 GET SINGLE CONFIG (requires READ access)
# ============================================================
@router.get("/{config_id}", response_model=ConfigResponse)
def get_config(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "CONFIGURATION", request)
    return config_controller.get_config_by_id(config_id, db)

# ============================================================
# 🔹 CREATE CONFIG (requires WRITE access)
# ============================================================
@router.post("/", response_model=ConfigResponse, status_code=201)
def create_config(
    config: ConfigCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "CONFIGURATION", request)
    return config_controller.create_config(config, db)

# ============================================================
# 🔹 UPDATE CONFIG (requires WRITE access)
# ============================================================
@router.put("/{config_id}", response_model=ConfigResponse)
def update_config(
    config_id: int,
    config: ConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "CONFIGURATION", request)
    return config_controller.update_config(config_id, config, db)

# ============================================================
# 🔹 DELETE CONFIG (requires WRITE access)
# ============================================================
@router.delete("/{config_id}")
def delete_config(
    config_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "CONFIGURATION", request)
    return config_controller.delete_config(config_id, db)
