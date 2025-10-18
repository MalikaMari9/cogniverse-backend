import os
import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.services.utils.upload_config import (
    PROFILE_IMAGES_DIR, 
    ALLOWED_IMAGE_TYPES, 
    MAX_FILE_SIZE,
    PROFILE_IMAGE_BASE_URL
)
import bcrypt  # 🆕 ADD THIS IMPORT


def get_user_profile(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def save_profile_image(profile_image: UploadFile) -> str:
    """Save profile image to disk and return the file URL"""
    
    # Validate file type
    if profile_image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
        )
    
    # Read file content
    file_content = profile_image.file.read()
    
    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # Generate unique filename
    file_extension = ALLOWED_IMAGE_TYPES[profile_image.content_type]
    filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = PROFILE_IMAGES_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # Return the URL path (not full path)
    return f"{PROFILE_IMAGE_BASE_URL}/{filename}"


def delete_old_profile_image(image_url: str):
    """Delete old profile image if it exists"""
    if image_url and image_url.startswith(PROFILE_IMAGE_BASE_URL):
        filename = image_url.split("/")[-1]
        old_file_path = PROFILE_IMAGES_DIR / filename
        if old_file_path.exists():
            try:
                old_file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete old profile image: {e}")


def update_user_profile(
    db: Session, 
    user_id: int, 
    username: str, 
    email: str, 
    profile_image: UploadFile = None
) -> User:
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Duplicate checks
    if db.query(User).filter(User.username == username, User.userid != user_id).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == email, User.userid != user_id).first():
        raise HTTPException(status_code=400, detail="Email already taken")

    # Update fields
    user.username = username
    user.email = email

    if profile_image:
        # Delete old profile image if it exists
        if user.profile_image_url:
            delete_old_profile_image(user.profile_image_url)
        
        # Save new profile image and get URL
        user.profile_image_url = save_profile_image(profile_image)

    db.commit()
    db.refresh(user)
    return user

# 🆕 ADD PASSWORD CHANGE FUNCTION
def change_user_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str
):
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password length
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    # Hash new password
    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update password
    user.password_hash = new_password_hash
    db.commit()
    
    return {"message": "Password updated successfully"}