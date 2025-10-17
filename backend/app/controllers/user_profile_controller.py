from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User


def get_user_profile(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user_profile(
    db: Session, user_id: int, username: str, email: str, profile_image: UploadFile = None
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
        # Optional: basic type check
        if profile_image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid image type")

        # Read file content as bytes
        user.profile_image_url = profile_image.read()

    db.commit()
    db.refresh(user)
    return user