from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.announcement_model import Announcement
from app.db.schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate

def get_all_announcements(db: Session):
    return db.query(Announcement).all()

def get_announcement_by_id(announcement_id: int, db: Session):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann

def create_announcement(announcement_data: AnnouncementCreate, db: Session, current_user_id: int):
    # Use the same parameter name as your working routes
    announcement_dict = announcement_data.model_dump()
    announcement_dict['created_by'] = current_user_id  # Set created_by to current user ID
    
    new_ann = Announcement(**announcement_dict)
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)
    return new_ann

def update_announcement(announcement_id: int, announcement_data: AnnouncementUpdate, db: Session, current_user_id: int):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    # Optional: Check if user owns this announcement or is admin
    # if ann.created_by != current_user_id:
    #     raise HTTPException(status_code=403, detail="Not authorized to edit this announcement")

    for key, value in announcement_data.model_dump(exclude_unset=True).items():
        setattr(ann, key, value)

    db.commit()
    db.refresh(ann)
    return ann

def delete_announcement(announcement_id: int, db: Session):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    db.delete(ann)
    db.commit()
    return {"detail": "Announcement deleted successfully"}