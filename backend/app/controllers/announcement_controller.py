from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.announcement_model import Announcement, LifecycleStatus
from app.db.models.user_model import User
from app.db.schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate

def get_all_announcements(db: Session):
    announcements = db.query(Announcement).all()
    
    # Add username to each announcement
    for announcement in announcements:
        if announcement.user:
            announcement.created_by_username = announcement.user.username
        else:
            announcement.created_by_username = "Unknown User"
    
    return announcements

def get_announcement_by_id(announcement_id: int, db: Session):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Add username
    if ann.user:
        ann.created_by_username = ann.user.username
    else:
        ann.created_by_username = "Unknown User"
    
    return ann

def create_announcement(announcement_data: AnnouncementCreate, db: Session, current_user_id: int):
    # Debug: Print incoming data
    print(f"🔍 DEBUG - Creating announcement with data:")
    print(f"  Title: {announcement_data.title}")
    print(f"  Content: {announcement_data.content}")
    print(f"  Status: {announcement_data.status}")
    print(f"  Status type: {type(announcement_data.status)}")
    print(f"  Current user ID: {current_user_id}")
    
    announcement_dict = announcement_data.model_dump()
    announcement_dict['created_by'] = current_user_id
    
    # Debug: Print the dictionary
    print(f"🔍 DEBUG - Announcement dict: {announcement_dict}")
    
    # Validate status
    if announcement_dict.get('status') not in [status.value for status in LifecycleStatus]:
        print(f"❌ DEBUG - Invalid status: {announcement_dict.get('status')}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {[status.value for status in LifecycleStatus]}"
        )
    
    try:
        new_ann = Announcement(**announcement_dict)
        db.add(new_ann)
        db.commit()
        db.refresh(new_ann)
        print(f"✅ DEBUG - Announcement created successfully with ID: {new_ann.announcementid}")
        
        # Add username to response
        if new_ann.user:
            new_ann.created_by_username = new_ann.user.username
        else:
            new_ann.created_by_username = "Unknown User"
        
        return new_ann
    except Exception as e:
        print(f"❌ DEBUG - Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def update_announcement(announcement_id: int, announcement_data: AnnouncementUpdate, db: Session, current_user_id: int):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    update_data = announcement_data.model_dump(exclude_unset=True)
    
    # Validate status if provided
    if 'status' in update_data and update_data['status'] not in [status.value for status in LifecycleStatus]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {[status.value for status in LifecycleStatus]}"
        )

    for key, value in update_data.items():
        setattr(ann, key, value)

    db.commit()
    db.refresh(ann)
    
    # Add username to response
    if ann.user:
        ann.created_by_username = ann.user.username
    else:
        ann.created_by_username = "Unknown User"
    
    return ann

def delete_announcement(announcement_id: int, db: Session):
    ann = db.query(Announcement).filter(Announcement.announcementid == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")

    db.delete(ann)
    db.commit()
    return {"detail": "Announcement deleted successfully"}