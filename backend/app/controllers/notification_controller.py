from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models.notification_model import Notification
from app.db.schemas.notification_schema import NotificationCreate, NotificationUpdate


# ============================================================
# 🔹 GET ALL NOTIFICATIONS
# ============================================================
def get_all_notifications(db: Session, include_deleted: bool = False):
    """Retrieve all notifications (exclude deleted by default)."""
    query = db.query(Notification)
    if not include_deleted:
        query = query.filter(Notification.is_deleted == False)
    return query.order_by(Notification.created_at.desc()).all()


# ============================================================
# 🔹 GET SINGLE NOTIFICATION
# ============================================================
def get_notification_by_id(notification_id: int, db: Session, include_deleted: bool = False):
    """Retrieve a single notification by ID."""
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n or (n.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Notification not found or deleted")
    return n


# ============================================================
# 🔹 CREATE NOTIFICATION
# ============================================================
def create_notification(notification_data: NotificationCreate, db: Session):
    """Create a new notification entry."""
    try:
        new_n = Notification(**notification_data.model_dump())
        db.add(new_n)
        db.commit()
        db.refresh(new_n)
        return new_n
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 UPDATE NOTIFICATION
# ============================================================
def update_notification(notification_id: int, notification_data: NotificationUpdate, db: Session):
    """Update a notification entry."""
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")

    if n.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted notification")

    update_fields = notification_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(n, key, value)

    db.commit()
    db.refresh(n)
    return n


# ============================================================
# 🔹 SOFT DELETE NOTIFICATION
# ============================================================
def delete_notification(notification_id: int, db: Session):
    """Soft delete a notification instead of removing it permanently."""
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")

    if n.is_deleted:
        raise HTTPException(status_code=400, detail="Notification already deleted")

    n.is_deleted = True
    n.deleted_at = datetime.utcnow()
    n.status = "inactive" if hasattr(n, "status") else None

    db.commit()
    return {"detail": f"Notification {notification_id} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE NOTIFICATION (Admin Only)
# ============================================================
def hard_delete_notification(notification_id: int, db: Session):
    """Permanently delete a notification (admin cleanup only)."""
    n = db.query(Notification).filter(Notification.notificationid == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(n)
    db.commit()
    return {"detail": f"Notification {notification_id} permanently deleted"}
