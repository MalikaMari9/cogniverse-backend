from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.announcement_schema import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
)
from app.controllers import announcement_controller
from app.db.database import get_db
from app.services.jwt_service import get_current_user
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.get("/", response_model=List[AnnouncementResponse])
async def get_all_announcements(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = announcement_controller.get_all_announcements(db)
        
        # Log announcement list view with deduplication
        if dedupe_service.should_log_action("ANNOUNCEMENT_LIST_VIEW", current_user.userid):
            announcement_count = len(result) if result else 0
            active_count = len([a for a in result if a.status == "active"]) if result else 0
            
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_LIST_VIEW",
                user_id=current_user.userid,
                details=f"Viewed announcements list ({announcement_count} total, {active_count} active)",
                request=request,
                status="active"
            )
        
        return result
        
    except Exception as e:
        # Log announcement list error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_LIST_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing announcements list: {str(e)}",
            request=request,
            status="active"
        )
        raise

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    request: Request,
    announcement_id: int, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = announcement_controller.get_announcement_by_id(announcement_id, db)
        
        # Log announcement view with deduplication
        cache_key = f"announcement_view_{announcement_id}"
        if dedupe_service.should_log_action("ANNOUNCEMENT_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_VIEW",
                user_id=current_user.userid,
                details=f"Viewed announcement: '{result.title}' (ID: {announcement_id})",
                request=request,
                status="active"
            )
        
        return result
        
    except Exception as e:
        # Log announcement view error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise

@router.post("/", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(
    request: Request,
    announcement: AnnouncementCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = announcement_controller.create_announcement(
            announcement_data=announcement, 
            db=db, 
            current_user_id=current_user.userid
        )
        
        # Log announcement creation with deduplication
        if dedupe_service.should_log_action("ANNOUNCEMENT_CREATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_CREATE",
                user_id=current_user.userid,
                details=f"Created announcement: '{announcement.title}' (Status: {announcement.status})",
                request=request,
                status="active"
            )
        
        return result
        
    except HTTPException as e:
        # Log announcement creation failure
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_CREATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to create announcement '{announcement.title}': {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log announcement creation error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_CREATE_ERROR",
            user_id=current_user.userid,
            details=f"Error creating announcement '{announcement.title}': {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    request: Request,
    announcement_id: int, 
    announcement: AnnouncementUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get current announcement data before update for logging
        current_announcement = announcement_controller.get_announcement_by_id(announcement_id, db)
        
        result = announcement_controller.update_announcement(
            announcement_id=announcement_id, 
            announcement_data=announcement, 
            db=db, 
            current_user_id=current_user.userid
        )
        
        # Log announcement update with deduplication
        if dedupe_service.should_log_action("ANNOUNCEMENT_UPDATE", current_user.userid):
            # Determine what fields were updated
            updated_fields = []
            if announcement.title is not None and announcement.title != current_announcement.title:
                updated_fields.append(f"title: '{current_announcement.title}'→'{announcement.title}'")
            if announcement.content is not None and announcement.content != current_announcement.content:
                content_preview_old = current_announcement.content[:50] + "..." if len(current_announcement.content) > 50 else current_announcement.content
                content_preview_new = announcement.content[:50] + "..." if len(announcement.content) > 50 else announcement.content
                updated_fields.append("content")
            if announcement.status is not None and announcement.status != current_announcement.status:
                updated_fields.append(f"status: {current_announcement.status}→{announcement.status}")
            
            update_details = f"Updated announcement: '{current_announcement.title}' (ID: {announcement_id})"
            if updated_fields:
                update_details += f" - Changes: {', '.join(updated_fields)}"
            
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_UPDATE",
                user_id=current_user.userid,
                details=update_details,
                request=request,
                status="active"
            )
        
        return result
        
    except HTTPException as e:
        # Log announcement update failure
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_UPDATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to update announcement ID {announcement_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log announcement update error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Error updating announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{announcement_id}")
async def delete_announcement(
    request: Request,
    announcement_id: int, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get announcement data before deletion for logging
        announcement = announcement_controller.get_announcement_by_id(announcement_id, db)
        
        result = announcement_controller.delete_announcement(announcement_id, db)
        
        # Log announcement deletion with deduplication
        if dedupe_service.should_log_action("ANNOUNCEMENT_DELETE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_DELETE",
                user_id=current_user.userid,
                details=f"Deleted announcement: '{announcement.title}' (ID: {announcement_id})",
                request=request,
                status="active"
            )
        
        return result
        
    except HTTPException as e:
        # Log announcement deletion failure
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to delete announcement ID {announcement_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log announcement deletion error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error deleting announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")