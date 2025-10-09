from fastapi import APIRouter, Depends, UploadFile, Form, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.user_profile_controller import (
    get_user_profile,
    update_user_profile,
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
@router.put("/profile", response_model=UserResponse)
def edit_profile(
    username: str = Form(...),
    email: str = Form(...),
    profile_image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_user_profile(db, current_user.userid, username, email, profile_image)

