from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.services.image_service import upload_image_to_s3


def get_user_profile(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user_profile(
    db: Session, user_id: int, username: str, email: str, image_file: UploadFile = None
) -> User:
    user = db.query(User).filter(User.userid == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Username / email checks
    if db.query(User).filter(User.username == username, User.userid != user_id).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    if db.query(User).filter(User.email == email, User.userid != user_id).first():
        raise HTTPException(status_code=400, detail="Email already taken")

    # Update fields
    user.username = username
    user.email = email

    if image_file:
        image_url = upload_image_to_s3(image_file)
        user.profile_image_url = image_url

    db.commit()
    db.refresh(user)
    return user
