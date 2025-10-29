import bcrypt
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.user_model import User, UserStatus
from app.db.schemas.user_schema import (
    UserAdminCreate,
    UserUpdate,
    UserAdminUpdate,
    UserStatusUpdate,
)
from app.db.schemas.user_schema import UserResponse
from app.services.utils.config_helper import get_config_value
from app.services.email_service import send_email_html
from math import ceil
from app.services.utils.config_helper import get_int_config
from sqlalchemy import or_, cast, String
# ============================================================
# 🔹 Get All Users
# ============================================================




def get_all_users_paginated(
    db: Session,
    page: int = 1,
    limit: Optional[int] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    q: Optional[str] = None,
):
    """Return users with pagination, filters, and keyword search."""
    if limit is None:
        limit = get_int_config(db, "LogPaginationLimit", 20)

    query = db.query(User).filter(User.is_deleted == False)

    # 🔍 Keyword search
    if q:
        q_like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                cast(User.username, String).ilike(q_like),
                cast(User.email, String).ilike(q_like),
                cast(User.role, String).ilike(q_like),
                cast(User.status, String).ilike(q_like),
            )
        )

    # ⚙️ Filters
    if status and status.lower() != "all":
        query = query.filter(cast(User.status, String).ilike(status))
    if role and role.lower() != "all":
        query = query.filter(cast(User.role, String).ilike(role))

    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 1,
    }

# ============================================================
# 🔹 Get User by ID
# ============================================================
def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# 🔹 Create User
# ============================================================


def create_user(db: Session, user_data: UserAdminCreate) -> User:
    """Create a new user and send a welcome email."""

    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # ✅ Use config default password if not provided
    raw_password = user_data.password or get_config_value(db, "defaultPassword", "Test12345")

    if not raw_password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    # Hash password
    password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Send welcome email
    try:
        frontend_base = get_config_value(db, "frontendBaseUrl", "http://localhost:5173")
        login_link = f"{frontend_base.rstrip('/')}/login"

        subject = "🎉 Welcome to CogniVerse!"
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background:#f9fafb; padding:20px;">
            <div style="max-width:500px; margin:auto; background:white; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); padding:30px;">
              <h2 style="color:#4a90e2;">Your CogniVerse Account is Ready!</h2>
              <p>Hello <b>{user.username}</b>,</p>
              <p>An administrator has created your CogniVerse account. You can now log in using:</p>
              <ul style="line-height:1.6;">
                <li><b>Username:</b> {user.email}</li>
                <li><b>Temporary Password:</b> {raw_password}</li>
              </ul>
              <p>Please log in and change your password immediately.</p>
              <p style="text-align:center; margin:25px 0;">
                <a href="{login_link}" style="background:#4a90e2; color:white; padding:10px 25px; border-radius:6px; text-decoration:none;">Go to Login</a>
              </p>
              <p style="font-size:13px; color:#999;">© {datetime.utcnow().year} CogniVerse. All rights reserved.</p>
            </div>
          </body>
        </html>
        """

        send_email_html(db, to_email=user.email, subject=subject, html_body=html)
        print(f"📧 Welcome email sent to {user.email}")

    except Exception as e:
        print(f"⚠️ Could not send welcome email: {e}")

    return user
# ============================================================
# 🔹 Update User (Non-Admin)
# ============================================================
def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update user profile (non-admin)"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check username and email uniqueness
    if user_data.username and user_data.username != user.username:
        if db.query(User).filter(User.username == user_data.username, User.userid != user_id).first():
            raise HTTPException(status_code=400, detail="Username already taken")

    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email, User.userid != user_id).first():
            raise HTTPException(status_code=400, detail="Email already taken")

    # Apply updates
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# ============================================================
# 🔹 Update User (Admin)
# ============================================================
def admin_update_user(db: Session, user_id: int, user_data: UserAdminUpdate) -> User:
    """Update user (admin version - can change role and status)"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Uniqueness checks
    if user_data.username and user_data.username != user.username:
        if db.query(User).filter(User.username == user_data.username, User.userid != user_id).first():
            raise HTTPException(status_code=400, detail="Username already taken")

    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email, User.userid != user_id).first():
            raise HTTPException(status_code=400, detail="Email already taken")

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# ============================================================
# 🔹 Change User Status
# ============================================================
def change_user_status(db: Session, user_id: int, status_data: UserStatusUpdate) -> User:
    """Change user status (active/suspended/deleted)"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = status_data.status
    db.commit()
    db.refresh(user)
    return user


# ============================================================
# 🔹 Soft Delete User
# ============================================================
def delete_user(db: Session, user_id: int, current_user_id: int) -> None:
    """Soft delete a user (sets both status='deleted' and is_deleted=True)"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_user = db.query(User).filter(User.userid == current_user_id).first()

    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    if current_user.role != "superadmin" and user.role in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="You do not have permission to delete admin users")

    user.status = UserStatus.deleted
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()

    db.commit()
    db.refresh(user)


# ============================================================
# 🔹 Hard Delete User
# ============================================================
def hard_delete_user(db: Session, user_id: int, current_user_id: int) -> None:
    """Permanently delete a user with protection"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_user = db.query(User).filter(User.userid == current_user_id).first()

    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    if current_user.role != "superadmin" and user.role in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Only superadmins can permanently delete admin users")

    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Could not permanently delete user due to database constraints: {str(e)}",
        )


# ============================================================
# 🔹 Bulk Change Status
# ============================================================
def bulk_change_status(db: Session, user_ids: List[int], new_status: UserStatus) -> dict:
    """Bulk change user status (skips deleted users)"""
    processed = 0
    failed = 0

    for user_id in user_ids:
        try:
            user = db.query(User).filter(User.userid == user_id).first()
            if user:
                if user.is_deleted or user.status == UserStatus.deleted:
                    failed += 1
                    continue

                user.status = new_status
                processed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    db.commit()

    return {"processed": processed, "failed": failed, "total": len(user_ids)}


# ============================================================
# 🔹 Bulk Soft Delete
# ============================================================
def bulk_delete_users(db: Session, user_ids: List[int]) -> dict:
    """Bulk soft delete users (sets status='deleted' and is_deleted=True)"""
    processed = 0
    failed = 0

    for user_id in user_ids:
        try:
            user = db.query(User).filter(User.userid == user_id).first()
            if user:
                user.status = UserStatus.deleted
                user.is_deleted = True
                user.deleted_at = datetime.utcnow()
                processed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    db.commit()

    return {"processed": processed, "failed": failed, "total": len(user_ids)}


# ============================================================
# 🔹 Restore User
# ============================================================
def restore_user(db: Session, user_id: int) -> User:
    """Restore a previously soft-deleted user"""
    user = db.query(User).filter(User.userid == user_id).first()
    if not user or not user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found or not deleted")

    user.is_deleted = False
    user.deleted_at = None
    user.status = UserStatus.active

    db.commit()
    db.refresh(user)
    return user
