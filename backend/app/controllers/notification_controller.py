from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.notification_model import Notification
from app.db.schemas.notification_schema import NotificationCreate, NotificationUpdate

def get_all_notifications(db: Session):
    return db.query(Notification).all()

def get_notification_by_id(notification_id: int, db: Session):
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n

def create_notification(notification_data: NotificationCreate, db: Session):
    new_n = Notification(**notification_data.model_dump())
    db.add(new_n)
    db.commit()
    db.refresh(new_n)
    return new_n

def update_notification(notification_id: int, notification_data: NotificationUpdate, db: Session):
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in notification_data.model_dump(exclude_unset=True).items():
        setattr(n, key, value)

    db.commit()
    db.refresh(n)
    return n

def delete_notification(notification_id: int, db: Session):
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(n)
    db.commit()
    return {"detail": "Notification deleted successfully"}
