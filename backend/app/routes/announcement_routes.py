from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.announcement_schema import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
)
from app.controllers import announcement_controller
from app.db.database import get_db
from app.services.jwt_service import get_current_user  # Use the same auth service

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.get("/", response_model=List[AnnouncementResponse])
def get_all_announcements(db: Session = Depends(get_db)):
    return announcement_controller.get_all_announcements(db)

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    return announcement_controller.get_announcement_by_id(announcement_id, db)

@router.post("/", response_model=AnnouncementResponse, status_code=201)
def create_announcement(
    announcement: AnnouncementCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth dependency
):
    # Pass the current user to the controller
    return announcement_controller.create_announcement(
        announcement_data=announcement, 
        db=db, 
        current_user_id=current_user.userid  # Use userid from your working routes
    )

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement(
    announcement_id: int, 
    announcement: AnnouncementUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth dependency
):
    return announcement_controller.update_announcement(
        announcement_id=announcement_id, 
        announcement_data=announcement, 
        db=db, 
        current_user_id=current_user.userid  # Use userid from your working routes
    )

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    return announcement_controller.delete_announcement(announcement_id, db)