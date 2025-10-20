# ===============================
# system_log_routes.py — Final Version
# ===============================
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.controllers import system_log_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user

router = APIRouter(prefix="/system-logs", tags=["System Logs"])


# ===============================
# 🔹 GET ALL LOGS
# ===============================
@router.get("/", response_model=List[SystemLogResponse])
def get_all_logs(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
    return system_log_controller.get_all_logs(db)


# ===============================
# 🔹 GET SINGLE LOG BY ID
# ===============================
@router.get("/{log_id}", response_model=SystemLogResponse)
def get_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
    return system_log_controller.get_log_by_id(log_id, db)


# ===============================
# 🔹 CREATE LOG (Internal or Manual)
# ===============================
@router.post("/", response_model=SystemLogResponse, status_code=201)
def create_log(
    log: SystemLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
    return system_log_controller.create_log(log, db)


# ===============================
# 🔹 DELETE SINGLE LOG
# ===============================
@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
    return system_log_controller.delete_log(log_id, db)


# ===============================
# 🔹 DELETE MULTIPLE LOGS (Bulk)
# ===============================
@router.delete("/")
def delete_logs_bulk(
    log_ids: List[int],
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
    return system_log_controller.delete_logs_bulk(log_ids, db)
