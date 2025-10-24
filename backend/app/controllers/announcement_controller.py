from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models.announcement_model import Announcement, LifecycleStatus
from app.db.models.user_model import User
from app.db.schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate


# ============================================================
# 🔹 GET ALL ANNOUNCEMENTS
# ============================================================
def get_all_announcements(db: Session, include_deleted: bool = False):
    """Retrieve all announcements (exclude deleted by default)."""
    query = db.query(Announcement)
    if not include_deleted:
        query = query.filter(Announcement.is_deleted == False)

    announcements = query.order_by(Announcement.created_at.desc()).all()

    # Add username to each announcement
    for ann in announcements:
        ann.created_by_username = ann.user.username if ann.user else "Unknown User"

    return announcements


# ============================================================
# 🔹 GET SINGLE ANNOUNCEMENT
# ============================================================
def get_announcement_by_id(announcement_id: int, db: Session, include_deleted: bool = False):
    """Retrieve a single announcement by ID."""
    ann = (
        db.query(Announcement)
        .filter(Announcement.announcementid == announcement_id)
        .first()
    )

    if not ann or (ann.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Announcement not found or deleted")

    ann.created_by_username = ann.user.username if ann.user else "Unknown User"
    return ann


# ============================================================
# 🔹 CREATE ANNOUNCEMENT
# ============================================================
def create_announcement(announcement_data: AnnouncementCreate, db: Session, current_user_id: int):
    """Create a new announcement."""
    ann_dict = announcement_data.model_dump()
    ann_dict["created_by"] = current_user_id

    # Validate status
    if ann_dict.get("status") not in [s.value for s in LifecycleStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {[s.value for s in LifecycleStatus]}",
        )

    try:
        new_ann = Announcement(**ann_dict)
        db.add(new_ann)
        db.commit()
        db.refresh(new_ann)

        new_ann.created_by_username = new_ann.user.username if new_ann.user else "Unknown User"
        return new_ann

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 UPDATE ANNOUNCEMENT
# ============================================================
def update_announcement(announcement_id: int, announcement_data: AnnouncementUpdate, db: Session, current_user_id: int):
    """Update announcement content."""
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if ann.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted announcement")

    update_data = announcement_data.model_dump(exclude_unset=True)

    # Validate status if provided
    if "status" in update_data and update_data["status"] not in [s.value for s in LifecycleStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {[s.value for s in LifecycleStatus]}",
        )

    for key, value in update_data.items():
        setattr(ann, key, value)

    db.commit()
    db.refresh(ann)

    ann.created_by_username = ann.user.username if ann.user else "Unknown User"
    return ann


# ============================================================
# 🔹 SOFT DELETE ANNOUNCEMENT
# ============================================================
def delete_announcement(announcement_id: int, db: Session):
    """Soft delete an announcement instead of removing it permanently."""
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if ann.is_deleted:
        raise HTTPException(status_code=400, detail="Announcement already deleted")

    ann.is_deleted = True
    ann.deleted_at = datetime.utcnow()
    ann.status = LifecycleStatus.inactive

    db.commit()
    return {"detail": f"Announcement {announcement_id} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE ANNOUNCEMENT (Admin Only)
# ============================================================
def hard_delete_announcement(announcement_id: int, db: Session):
    """Permanently delete an announcement (use only for admin cleanup)."""
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    db.delete(ann)
    db.commit()
    return {"detail": f"Announcement {announcement_id} permanently deleted"}
