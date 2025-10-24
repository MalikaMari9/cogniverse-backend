# ===============================
# app/routes/user_management_routes.py — Final Version
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
    hard_delete_user, bulk_change_status, bulk_delete_users,
    restore_user
)
from app.services.jwt_service import get_current_user
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service
from app.services.utils.permissions_helper import enforce_permission_auto
from app.db.models.user_model import User

router = APIRouter(prefix="/admin/users", tags=["User Management"])


# ============================================================
# 🔹 Get All Users
# ============================================================
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
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)

        skip = (page - 1) * page_size
        users = get_all_users(db, skip=skip, limit=page_size, status=status, role=role)
        total_users = db.query(User).count()

        if dedupe_service.should_log_action("USER_LIST_VIEW", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="USER_LIST_VIEW",
                user_id=current_user.userid,
                details=f"Viewed user list (page {page}, status={status}, role={role})",
                request=request,
                status="active"
            )

        return {"users": users, "total": total_users, "page": page, "page_size": page_size}

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


# ============================================================
# 🔹 Get User by ID
# ============================================================
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

        cache_key = f"user_view_{user_id}"
        if dedupe_service.should_log_action("USER_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="USER_VIEW",
                user_id=current_user.userid,
                details=f"Viewed user ID {user_id} ({user.username})",
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


# ============================================================
# 🔹 Create User
# ============================================================
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

        await system_logger.log_action(
            db=db,
            action_type="USER_CREATE",
            user_id=current_user.userid,
            details=f"Created new user: {user.username} ({user.email}) with role {user.role}",
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


# ============================================================
# 🔹 Update User (Admin)
# ============================================================
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

        updated_fields = []
        if user_data.username and user_data.username != current_user_data.username:
            updated_fields.append(f"username: {current_user_data.username}→{user_data.username}")
        if user_data.email and user_data.email != current_user_data.email:
            updated_fields.append(f"email: {current_user_data.email}→{user_data.email}")
        if user_data.role and user_data.role != current_user_data.role:
            updated_fields.append(f"role: {current_user_data.role}→{user_data.role}")
        if user_data.status and user_data.status != current_user_data.status:
            updated_fields.append(f"status: {current_user_data.status}→{user_data.status}")

        change_summary = ", ".join(updated_fields) if updated_fields else "no visible field changes"
        await system_logger.log_action(
            db=db,
            action_type="USER_UPDATE",
            user_id=current_user.userid,
            details=f"Updated user {user_id} ({current_user_data.username}): {change_summary}",
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


# ============================================================
# 🔹 Change User Status
# ============================================================
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
        change_user_status(db, user_id, status_data)

        await system_logger.log_action(
            db=db,
            action_type="USER_STATUS_CHANGE",
            user_id=current_user.userid,
            details=f"Changed status of user {user_id} ({current_user_data.username}) to {status_data.status}",
            request=request,
            status="active"
        )

        return {"message": f"User status updated to {status_data.status}", "user_id": user_id, "new_status": status_data.status}

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_STATUS_CHANGE_ERROR",
            user_id=current_user.userid,
            details=f"Error changing status of user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Soft Delete User
# ============================================================
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
        delete_user(db, user_id, current_user.userid)

        await system_logger.log_action(
            db=db,
            action_type="USER_DELETE",
            user_id=current_user.userid,
            details=f"Soft deleted user {user_id} ({user.username})",
            request=request,
            status="active"
        )
        return {"message": f"User {user_id} soft-deleted successfully"}

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


# ============================================================
# 🔹 Restore User
# ============================================================
@router.post("/{user_id}/restore", response_model=MessageResponse)
async def restore_deleted_user(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore a previously soft-deleted user"""
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)
        user = restore_user(db, user_id)

        await system_logger.log_action(
            db=db,
            action_type="USER_RESTORE",
            user_id=current_user.userid,
            details=f"Restored user {user_id} ({user.username})",
            request=request,
            status="active"
        )
        return {"message": f"User {user.username} has been restored successfully"}

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="USER_RESTORE_ERROR",
            user_id=current_user.userid,
            details=f"Error restoring user {user_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================
# 🔹 Hard Delete User
# ============================================================
@router.delete("/{user_id}/hard", response_model=MessageResponse)
async def hard_delete_user_route(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)
        user = get_user_by_id(db, user_id)
        hard_delete_user(db, user_id, current_user.userid)

        await system_logger.log_action(
            db=db,
            action_type="USER_HARD_DELETE",
            user_id=current_user.userid,
            details=f"Permanently deleted user {user_id} ({user.username})",
            request=request,
            status="active"
        )
        return {"message": f"User {user.username} permanently deleted"}

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


# ============================================================
# 🔹 Bulk Status Change
# ============================================================
@router.post("/bulk/status", response_model=BulkOperationResponse)
async def bulk_update_status(
    request: Request,
    operation: BulkUserOperation,
    status: UserStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)
        result = bulk_change_status(db, operation.user_ids, status.status)

        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_STATUS_CHANGE",
            user_id=current_user.userid,
            details=f"Bulk updated status of {result['processed']} users to {status.status}",
            request=request,
            status="active"
        )
        return result

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


# ============================================================
# 🔹 Bulk Soft Delete
# ============================================================
@router.post("/bulk/delete", response_model=BulkOperationResponse)
async def bulk_delete_users_route(
    request: Request,
    operation: BulkUserOperation,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "USER_MANAGEMENT", request)
        result = bulk_delete_users(db, operation.user_ids)

        await system_logger.log_action(
            db=db,
            action_type="USER_BULK_DELETE",
            user_id=current_user.userid,
            details=f"Bulk soft deleted {result['processed']} users (failed: {result['failed']})",
            request=request,
            status="active"
        )
        return result

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
