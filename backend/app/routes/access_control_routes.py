from fastapi import APIRouter, Depends, Request
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

router = APIRouter(prefix="/access-controls", tags=["Access Controls"])

# ============================================================
# 🔹 GET ALL ACCESS CONTROLS (requires READ access)
# ============================================================
@router.get("/", response_model=List[AccessControlResponse])
def get_all_access_controls(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
    return access_control_controller.get_all_access_controls(db)


# ============================================================
# 🔹 GET SINGLE ACCESS CONTROL (requires READ access)
# ============================================================
@router.get("/{access_id}", response_model=AccessControlResponse)
def get_access_control(
    access_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
    return access_control_controller.get_access_by_id(access_id, db)


# ============================================================
# 🔹 CREATE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.post("/", response_model=AccessControlResponse, status_code=201)
def create_access_control(
    access: AccessControlCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
    return access_control_controller.create_access_control(access, db)


# ============================================================
# 🔹 UPDATE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.put("/{access_id}", response_model=AccessControlResponse)
def update_access_control(
    access_id: int,
    access: AccessControlUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
    return access_control_controller.update_access_control(access_id, access, db)


# ============================================================
# 🔹 DELETE ACCESS CONTROL (requires WRITE access)
# ============================================================
@router.delete("/{access_id}")
def delete_access_control(
    access_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_permission_auto(db, current_user, "ACCESS_CONTROL", request)
    return access_control_controller.delete_access_control(access_id, db)
