# ===============================
# system_log_routes.py — Final Version
# ===============================
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.controllers import system_log_controller
from app.db.database import get_db
from app.services.utils.permissions_helper import enforce_permission_auto
from app.services.jwt_service import get_current_user
from app.db.models.system_log_model import SystemLog
from math import ceil
from app.services.utils.config_helper import get_int_config
router = APIRouter(prefix="/system-logs", tags=["System Logs"])


# ===============================
# 🔹 GET ALL LOGS (Paginated)
# ===============================
@router.get("/", response_model=dict)
def get_all_logs(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, description="Items per page"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.get_all_logs_paginated(db, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
