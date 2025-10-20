# ===============================
# app/routes/announcement_routes.py — Final Polished Version
# ===============================

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
from app.services.utils.permissions_helper import enforce_permission_auto


router = APIRouter(prefix="/announcements", tags=["Announcements"])


# ===============================
# 🔹 Get All Announcements
# ===============================
@router.get("/", response_model=List[AnnouncementResponse])
async def get_all_announcements(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Check permission first
        enforce_permission_auto(db, current_user, "ANNOUNCEMENTS", request)

        result = announcement_controller.get_all_announcements(db)

        # 🪶 Deduped log
        if dedupe_service.should_log_action("ANNOUNCEMENT_LIST_VIEW", current_user.userid):
            total = len(result or [])
            active = len([a for a in result if a.status == "active"])
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_LIST_VIEW",
                user_id=current_user.userid,
                details=f"Viewed announcements list ({total} total, {active} active)",
                request=request,
                status="active"
            )

        return result

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_LIST_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing announcements list: {str(e)}",
            request=request,
            status="active"
        )
        raise


# ===============================
# 🔹 Get Single Announcement
# ===============================
@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    request: Request,
    announcement_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "ANNOUNCEMENTS", request)

        result = announcement_controller.get_announcement_by_id(announcement_id, db)

        cache_key = f"announcement_view_{announcement_id}"
        if dedupe_service.should_log_action("ANNOUNCEMENT_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_VIEW",
                user_id=current_user.userid,
                details=f"Viewed announcement '{result.title}' (ID: {announcement_id})",
                request=request,
                status="active"
            )

        return result

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise


# ===============================
# 🔹 Create Announcement
# ===============================
@router.post("/", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(
    request: Request,
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        enforce_permission_auto(db, current_user, "ANNOUNCEMENTS", request)

        result = announcement_controller.create_announcement(
            announcement_data=announcement,
            db=db,
            current_user_id=current_user.userid
        )

        if dedupe_service.should_log_action("ANNOUNCEMENT_CREATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_CREATE",
                user_id=current_user.userid,
                details=f"Created announcement '{announcement.title}' (Status: {announcement.status})",
                request=request,
                status="active"
            )

        return result

    except HTTPException as e:
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
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_CREATE_ERROR",
            user_id=current_user.userid,
            details=f"Error creating announcement '{announcement.title}': {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Update Announcement
# ===============================
@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    request: Request,
    announcement_id: int,
    announcement: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        enforce_permission_auto(db, current_user, "ANNOUNCEMENTS", request)

        current_announcement = announcement_controller.get_announcement_by_id(announcement_id, db)
        result = announcement_controller.update_announcement(
            announcement_id=announcement_id,
            announcement_data=announcement,
            db=db,
            current_user_id=current_user.userid
        )

        if dedupe_service.should_log_action("ANNOUNCEMENT_UPDATE", current_user.userid):
            updated_fields = []
            if announcement.title and announcement.title != current_announcement.title:
                updated_fields.append(f"title: '{current_announcement.title}'→'{announcement.title}'")
            if announcement.status and announcement.status != current_announcement.status:
                updated_fields.append(f"status: {current_announcement.status}→{announcement.status}")
            if announcement.content and announcement.content != current_announcement.content:
                updated_fields.append("content changed")

            update_details = (
                f"Updated announcement '{current_announcement.title}' (ID: {announcement_id})"
            )
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
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Error updating announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Delete Announcement
# ===============================
@router.delete("/{announcement_id}")
async def delete_announcement(
    request: Request,
    announcement_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "ANNOUNCEMENTS", request)

        announcement = announcement_controller.get_announcement_by_id(announcement_id, db)
        result = announcement_controller.delete_announcement(announcement_id, db)

        if dedupe_service.should_log_action("ANNOUNCEMENT_DELETE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="ANNOUNCEMENT_DELETE",
                user_id=current_user.userid,
                details=f"Deleted announcement '{announcement.title}' (ID: {announcement_id})",
                request=request,
                status="active"
            )

        return result

    except HTTPException as e:
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
        await system_logger.log_action(
            db=db,
            action_type="ANNOUNCEMENT_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error deleting announcement ID {announcement_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
