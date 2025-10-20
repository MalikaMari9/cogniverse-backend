# ===============================
# app/routes/user_management_routes.py — Fixed Version
# ===============================

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.schemas.user_schema import (
    UserCreate, UserUpdate, UserAdminUpdate, UserStatusUpdate,
    UserResponse, UserListResponse, MessageResponse,
    UserStatusResponse, BulkUserOperation, BulkOperationResponse
)
from app.controllers.user_management_controller import (
    get_all_users, get_user_by_id, create_user, update_user,
    admin_update_user, change_user_status, delete_user,
    hard_delete_user, bulk_change_status, bulk_delete_users
)
from app.services.jwt_service import get_current_user
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service
from app.services.utils.permissions_helper import enforce_permission_auto
from app.db.models.user_model import User  # Add this import for the total count query

router = APIRouter(prefix="/admin/users", tags=["User Management"])


# ===============================
# 🔹 Get All Users
# ===============================
@router.get("/", response_model=UserListResponse)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Check permission first
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        skip = (page - 1) * page_size
        users = get_all_users(db, skip=skip, limit=page_size, status=status, role=role)
        total_users = db.query(User).count()
        
        # Log user list view with deduplication
        if dedupe_service.should_log_action("USER_LIST_VIEW", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="USER_LIST_VIEW",
                user_id=current_user.userid,
                details=f"Viewed user list (page {page}, status: {status}, role: {role})",
                request=request,
                status="active"
            )
        
        return {
            "users": users,
            "total": total_users,
            "page": page,
            "page_size": page_size
        }
        
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_LIST_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing user list: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Get User By ID
# ===============================
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        user = get_user_by_id(db, user_id)
        
        # Log user view with deduplication
        cache_key = f"user_view_{user_id}"
        if dedupe_service.should_log_action("USER_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="USER_VIEW",
                user_id=current_user.userid,
                details=f"Viewed user ID: {user_id} ({user.username})",
                request=request,
                status="active"
            )
        
        return user
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_VIEW_FAILED",
            user_id=current_user.userid,
            details=f"Failed to view user {user_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Create User
# ===============================
@router.post("/", response_model=UserResponse, status_code=201)
async def create_new_user(
    request: Request,
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        user = create_user(db, user_data)
        
        # Log user creation
        await system_logger.log_action(
            db=db,
            action_type="USER_CREATE",
            user_id=current_user.userid,
            details=f"Created new user: {user.username} ({user.email}) with role: {user.role}",
            request=request,
            status="active"
        )
        
        return user
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_CREATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to create user {user_data.username}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_CREATE_ERROR",
            user_id=current_user.userid,
            details=f"Error creating user {user_data.username}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Update User (Admin)
# ===============================
@router.put("/{user_id}", response_model=UserResponse)
async def update_user_admin(
    request: Request,
    user_id: int,
    user_data: UserAdminUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        current_user_data = get_user_by_id(db, user_id)
        user = admin_update_user(db, user_id, user_data)
        
        # Log user update
        updated_fields = []
        if user_data.username and user_data.username != current_user_data.username:
            updated_fields.append(f"username: '{current_user_data.username}'→'{user_data.username}'")
        if user_data.email and user_data.email != current_user_data.email:
            updated_fields.append(f"email: '{current_user_data.email}'→'{user_data.email}'")
        if user_data.role and user_data.role != current_user_data.role:
            updated_fields.append(f"role: {current_user_data.role}→{user_data.role}")
        if user_data.status and user_data.status != current_user_data.status:
            updated_fields.append(f"status: {current_user_data.status}→{user_data.status}")

        update_details = f"Updated user ID {user_id} ({current_user_data.username})"
        if updated_fields:
            update_details += f" - Changes: {', '.join(updated_fields)}"

        await system_logger.log_action(
            db=db,
            action_type="USER_UPDATE",
            user_id=current_user.userid,
            details=update_details,
            request=request,
            status="active"
        )
        
        return user
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_UPDATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to update user {user_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Error updating user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Change User Status
# ===============================
@router.patch("/{user_id}/status", response_model=UserStatusResponse)
async def update_user_status(
    request: Request,
    user_id: int,
    status_data: UserStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        current_user_data = get_user_by_id(db, user_id)
        user = change_user_status(db, user_id, status_data)
        
        # Log status change
        await system_logger.log_action(
            db=db,
            action_type="USER_STATUS_CHANGE",
            user_id=current_user.userid,
            details=f"Changed user {user_id} ({current_user_data.username}) status from {current_user_data.status} to {status_data.status}",
            request=request,
            status="active"
        )
        
        return {
            "message": f"User status updated to {status_data.status}",
            "user_id": user_id,
            "new_status": status_data.status
        }
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_STATUS_CHANGE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to change user {user_id} status: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_STATUS_CHANGE_ERROR",
            user_id=current_user.userid,
            details=f"Error changing user {user_id} status: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Delete User (Soft)
# ===============================
@router.delete("/{user_id}", response_model=MessageResponse)
async def soft_delete_user(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        user = get_user_by_id(db, user_id)
        delete_user(db, user_id)
        
        # Log user deletion
        await system_logger.log_action(
            db=db,
            action_type="USER_DELETE",
            user_id=current_user.userid,
            details=f"Soft deleted user ID: {user_id} ({user.username})",
            request=request,
            status="active"
        )
        
        return {"message": f"User {user_id} has been deleted"}
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to delete user {user_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error deleting user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Hard Delete User
# ===============================
@router.delete("/{user_id}/hard", response_model=MessageResponse)
async def permanent_delete_user(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        user = get_user_by_id(db, user_id)
        hard_delete_user(db, user_id)
        
        # Log hard deletion
        await system_logger.log_action(
            db=db,
            action_type="USER_HARD_DELETE",
            user_id=current_user.userid,
            details=f"Permanently deleted user ID: {user_id} ({user.username})",
            request=request,
            status="active"
        )
        
        return {"message": f"User {user_id} has been permanently deleted"}
        
    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_HARD_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to hard delete user {user_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_HARD_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error hard deleting user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Bulk Status Change
# ===============================
@router.post("/bulk/status", response_model=BulkOperationResponse)
async def bulk_update_user_status(
    request: Request,
    operation: BulkUserOperation,
    status: UserStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        result = bulk_change_status(db, operation.user_ids, status.status)
        
        # Log bulk status change
        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_STATUS_CHANGE",
            user_id=current_user.userid,
            details=f"Bulk status change: {len(operation.user_ids)} users to {status.status} (processed: {result['processed']}, failed: {result['failed']})",
            request=request,
            status="active"
        )
        
        return {
            "message": f"Bulk status update completed",
            "processed": result["processed"],
            "failed": result["failed"]
        }
        
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_STATUS_CHANGE_ERROR",
            user_id=current_user.userid,
            details=f"Error in bulk status change: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Bulk Delete
# ===============================
@router.post("/bulk/delete", response_model=BulkOperationResponse)
async def bulk_delete_users_endpoint(
    request: Request,
    operation: BulkUserOperation,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        result = bulk_delete_users(db, operation.user_ids)
        
        # Log bulk deletion
        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_DELETE",
            user_id=current_user.userid,
            details=f"Bulk deleted {len(operation.user_ids)} users (processed: {result['processed']}, failed: {result['failed']})",
            request=request,
            status="active"
        )
        
        return {
            "message": "Bulk deletion completed",
            "processed": result["processed"],
            "failed": result["failed"]
        }
        
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error in bulk deletion: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")