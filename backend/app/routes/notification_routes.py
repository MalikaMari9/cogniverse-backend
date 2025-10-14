from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.notification_schema import (
    NotificationCreate, NotificationUpdate, NotificationResponse
)
from app.controllers import notification_controller
from app.db.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
def get_all_notifications(db: Session = Depends(get_db)):
    return notification_controller.get_all_notifications(db)

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    return notification_controller.get_notification_by_id(notification_id, db)

@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    return notification_controller.create_notification(notification, db)

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: int, notification: NotificationUpdate, db: Session = Depends(get_db)):
    return notification_controller.update_notification(notification_id, notification, db)

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    return notification_controller.delete_notification(notification_id, db)
