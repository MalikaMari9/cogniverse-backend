# ===============================
# app/routes/system_log_routes.py — Final Unified Version
# ===============================

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.controllers import system_log_controller
from app.db.database import get_db
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto

router = APIRouter(prefix="/system-logs", tags=["System Logs"])


# ============================================================
# 🔹 GET ALL LOGS (Paginated + Search)
# ============================================================
@router.get("/", response_model=dict)
def get_all_logs(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(None, ge=1, description="Items per page (from config if not provided)"),
    q: Optional[str] = Query(None, description="Optional search keyword (username, action, details, status)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return paginated system logs.
    Supports search by username, action_type, details, or status.
    """
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.get_all_logs_paginated(db=db, page=page, limit=limit, q=q)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system logs: {str(e)}")


# ============================================================
# 🔹 GET SINGLE LOG BY ID
# ============================================================
@router.get("/{log_id}", response_model=SystemLogResponse)
def get_log_by_id(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return a specific system log by ID.
    """
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.get_log_by_id(db=db, log_id=log_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch log #{log_id}: {str(e)}")


# ============================================================
# 🔹 CREATE LOG (Manual or Internal)
# ============================================================
@router.post("/", response_model=SystemLogResponse, status_code=201)
def create_log(
    log_data: SystemLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new log manually (admin usage) or programmatically.
    """
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.create_log(db=db, log_data=log_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create system log: {str(e)}")


# ============================================================
# 🔹 DELETE MULTIPLE LOGS (Bulk)
# ============================================================
@router.delete("/", response_model=dict)
def delete_logs_bulk(
    log_ids: List[int],
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete multiple system logs at once.
    """
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.delete_logs_bulk(db=db, log_ids=log_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logs: {str(e)}")


# ============================================================
# 🔹 DELETE SINGLE LOG
# ============================================================
@router.delete("/{log_id}", response_model=dict)
def delete_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a single log by ID.
    """
    try:
        enforce_permission_auto(db, current_user, "SYSTEM_LOGS", request)
        return system_log_controller.delete_log(db=db, log_id=log_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete log #{log_id}: {str(e)}")
