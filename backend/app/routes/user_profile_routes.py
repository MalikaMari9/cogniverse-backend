from fastapi import APIRouter, Depends, UploadFile, Form, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user_model import User
from app.controllers.user_profile_controller import (
    get_user_profile,
    update_user_profile,
    save_profile_image,
    delete_old_profile_image,
)
from app.services.jwt_service import get_current_user
from app.db.schemas.user_schema import UserResponse

router = APIRouter(prefix="/users", tags=["User Profile"])

# -------- VIEW PROFILE --------
@router.get("/profile", response_model=UserResponse)
def view_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_user_profile(db, current_user.userid)

# -------- EDIT PROFILE --------
@router.put("/profile", response_model=UserResponse)  # 🟢 MAKE SURE THIS IS PUT
def edit_profile(
    username: str = Form(...),
    email: str = Form(...),
    profile_image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print(f"🎯 PUT /users/profile endpoint called for user {current_user.userid}")
    return update_user_profile(
        db=db,
        user_id=current_user.userid,
        username=username,
        email=email,
        profile_image=profile_image,
    )

# -------- UPLOAD PROFILE PICTURE ONLY --------
@router.put("/profile/picture", response_model=UserResponse)
async def upload_profile_picture(
    profile_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload only the profile picture (separate from other profile data)"""
    user = db.query(User).filter(User.userid == current_user.userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile_image:
        # Delete old profile image if it exists
        if user.profile_image_url:
            delete_old_profile_image(user.profile_image_url)
        
        # Save new profile image and get URL
        user.profile_image_url = save_profile_image(profile_image)
        
        db.commit()
        db.refresh(user)
    
    return user

# -------- DELETE PROFILE PICTURE --------
@router.delete("/profile/picture", response_model=UserResponse)
async def delete_profile_picture(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the user's profile picture"""
    user = db.query(User).filter(User.userid == current_user.userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.profile_image_url:
        delete_old_profile_image(user.profile_image_url)
        user.profile_image_url = None
        
        db.commit()
        db.refresh(user)
    
    return user

# -------- TEST ENDPOINT --------
@router.get("/test")
def test_endpoint():
    return {"message": "Users router is working!"}

# 🆕 ADD THIS: Test PUT endpoint
@router.put("/test-put")
def test_put_endpoint(
    username: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "✅ PUT endpoint works!", 
        "username_received": username,
        "user_id": current_user.userid
    }