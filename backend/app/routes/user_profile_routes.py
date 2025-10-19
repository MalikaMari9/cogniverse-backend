from fastapi import APIRouter, Depends, UploadFile, Form, File, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user_model import User
from app.controllers.user_profile_controller import (
    get_user_profile,
    update_user_profile,
    save_profile_image,
    delete_old_profile_image,
    change_user_password,
)
from app.services.jwt_service import get_current_user
from app.db.schemas.user_schema import UserResponse, PasswordChangeRequest, PasswordChangeResponse
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service  # Import the deduplication service

router = APIRouter(prefix="/users", tags=["User Profile"])

# -------- VIEW PROFILE --------
@router.get("/profile", response_model=UserResponse)
async def view_profile(
    request: Request,
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        result = get_user_profile(db, current_user.userid)
        
        # Log profile view with deduplication
        if dedupe_service.should_log_action("PROFILE_VIEW", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="PROFILE_VIEW",
                user_id=current_user.userid,
                details="User viewed their profile",
                request=request,
                status="active"
            )
        
        return result
        
    except Exception as e:
        # Log profile view error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing profile: {str(e)}",
            request=request,
            status="active"
        )
        raise

# -------- EDIT PROFILE --------
@router.put("/profile", response_model=UserResponse)
async def edit_profile(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    profile_image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        print(f"🎯 PUT /users/profile endpoint called for user {current_user.userid}")
        result = update_user_profile(
            db=db,
            user_id=current_user.userid,
            username=username,
            email=email,
            profile_image=profile_image,
        )
        
        # Log profile update with deduplication
        if dedupe_service.should_log_action("PROFILE_UPDATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="PROFILE_UPDATE",
                user_id=current_user.userid,
                details=f"User updated profile: username={username}, email={email}",
                request=request,
                status="active"
            )
        
        return result
        
    except HTTPException as e:
        # Log profile update failure (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_UPDATE_FAILED",
            user_id=current_user.userid,
            details=f"Profile update failed: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log profile update error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Profile update error: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

# -------- UPLOAD PROFILE PICTURE ONLY --------
@router.put("/profile/picture", response_model=UserResponse)
async def upload_profile_picture(
    request: Request,
    profile_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload only the profile picture (separate from other profile data)"""
    try:
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
        
        # Log profile picture upload with deduplication
        if dedupe_service.should_log_action("PROFILE_PICTURE_UPLOAD", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="PROFILE_PICTURE_UPLOAD",
                user_id=current_user.userid,
                details="User uploaded new profile picture",
                request=request,
                status="active"
            )
        
        return user
        
    except HTTPException as e:
        # Log upload failure (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_PICTURE_UPLOAD_FAILED",
            user_id=current_user.userid,
            details=f"Profile picture upload failed: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log upload error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_PICTURE_UPLOAD_ERROR",
            user_id=current_user.userid,
            details=f"Profile picture upload error: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

# -------- DELETE PROFILE PICTURE --------
@router.delete("/profile/picture", response_model=UserResponse)
async def delete_profile_picture(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the user's profile picture"""
    try:
        user = db.query(User).filter(User.userid == current_user.userid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.profile_image_url:
            delete_old_profile_image(user.profile_image_url)
            user.profile_image_url = None
            
            db.commit()
            db.refresh(user)
        
        # Log profile picture deletion with deduplication
        if dedupe_service.should_log_action("PROFILE_PICTURE_DELETE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="PROFILE_PICTURE_DELETE",
                user_id=current_user.userid,
                details="User deleted profile picture",
                request=request,
                status="active"
            )
        
        return user
        
    except HTTPException as e:
        # Log deletion failure (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_PICTURE_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Profile picture deletion failed: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log deletion error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PROFILE_PICTURE_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Profile picture deletion error: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

# 🆕 ADD PASSWORD CHANGE ROUTE
@router.put("/profile/password", response_model=PasswordChangeResponse)
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password with old password verification"""
    try:
        result = change_user_password(
            db=db,
            user_id=current_user.userid,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        # Log password change with deduplication
        if dedupe_service.should_log_action("PASSWORD_CHANGE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="PASSWORD_CHANGE",
                user_id=current_user.userid,
                details="User changed password successfully",
                request=request,
                status="active"
            )
        
        return result
        
    except HTTPException as e:
        # Log password change failure (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PASSWORD_CHANGE_FAILED",
            user_id=current_user.userid,
            details=f"Password change failed: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log password change error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="PASSWORD_CHANGE_ERROR",
            user_id=current_user.userid,
            details=f"Password change error: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

# -------- TEST ENDPOINT --------
@router.get("/test")
async def test_endpoint(
    request: Request,
    db: Session = Depends(get_db)
):
    # Log test endpoint access (no deduplication for test endpoints)
    await system_logger.log_action(
        db=db,
        action_type="TEST_ENDPOINT_ACCESS",
        user_id=None,
        details="Test endpoint accessed",
        request=request,
        status="active"
    )
    
    return {"message": "Users router is working!"}

@router.put("/test-put")
async def test_put_endpoint(
    request: Request,
    username: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Log test PUT endpoint (no deduplication for test endpoints)
    await system_logger.log_action(
        db=db,
        action_type="TEST_PUT_ENDPOINT",
        user_id=current_user.userid,
        details=f"Test PUT endpoint called with username: {username}",
        request=request,
        status="active"
    )
    
    return {
        "message": "✅ PUT endpoint works!", 
        "username_received": username,
        "user_id": current_user.userid
    }