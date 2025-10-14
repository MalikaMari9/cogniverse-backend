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

def create_announcement(announcement_data: AnnouncementCreate, db: Session):
    new_ann = Announcement(**announcement_data.model_dump())
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)
    return new_ann

def update_announcement(announcement_id: int, announcement_data: AnnouncementUpdate, db: Session):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

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
