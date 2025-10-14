from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.announcement_schema import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
)
from app.controllers import announcement_controller
from app.db.database import get_db

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.get("/", response_model=List[AnnouncementResponse])
def get_all_announcements(db: Session = Depends(get_db)):
    return announcement_controller.get_all_announcements(db)

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    return announcement_controller.get_announcement_by_id(announcement_id, db)

@router.post("/", response_model=AnnouncementResponse, status_code=201)
def create_announcement(announcement: AnnouncementCreate, db: Session = Depends(get_db)):
    return announcement_controller.create_announcement(announcement, db)

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(announcement_id: int, announcement: AnnouncementUpdate, db: Session = Depends(get_db)):
    return announcement_controller.update_announcement(announcement_id, announcement, db)

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    return announcement_controller.delete_announcement(announcement_id, db)
