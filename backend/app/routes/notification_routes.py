# ===============================
# app/routes/notification_routes.py — Soft Delete Ready
# ===============================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.schemas.notification_schema import (
    NotificationCreate, NotificationUpdate, NotificationResponse
)
from app.controllers import notification_controller
from app.db.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ===============================
# 🔹 Get All Notifications
# ===============================
@router.get("/", response_model=List[NotificationResponse])
def get_all_notifications(
    db: Session = Depends(get_db),
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted notifications"),
):
    return notification_controller.get_all_notifications(db, include_deleted=include_deleted)


# ===============================
# 🔹 Get Notification by ID
# ===============================
@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted notification"),
):
    return notification_controller.get_notification_by_id(notification_id, db, include_deleted=include_deleted)


# ===============================
# 🔹 Create Notification
# ===============================
@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
):
    return notification_controller.create_notification(notification, db)


# ===============================
# 🔹 Update Notification
# ===============================
@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db),
):
    return notification_controller.update_notification(notification_id, notification, db)


# ===============================
# 🔹 Soft Delete Notification
# ===============================
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
):
    return notification_controller.delete_notification(notification_id, db)


# ===============================
# 🔹 Hard Delete (Admin Cleanup)
# ===============================
@router.delete("/{notification_id}/purge")
def hard_delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
):
    """Permanent deletion for admin or maintenance cleanup."""
    return notification_controller.hard_delete_notification(notification_id, db)
