import bcrypt
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.user_model import User, UserStatus
from app.db.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserAdminUpdate,
    UserStatusUpdate,
)


# ============================================================
# 🔹 Get All Users
# ============================================================
def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    role: Optional[str] = None,
) -> List[User]:
    """Get all users with optional filtering"""
    query = db.query(User)

    if status:
        query = query.filter(User.status == UserStatus(status))
    if role:
        query = query.filter(User.role == role)

    return query.offset(skip).limit(limit).all()


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
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    password_hash = bcrypt.hashpw(
        user_data.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

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
