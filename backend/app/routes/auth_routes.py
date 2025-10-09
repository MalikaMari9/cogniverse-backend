from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.auth_controller import register_user, login_user, logout_user
from app.services.jwt_service import get_current_user, security
from app.db.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -------- REGISTER --------
@router.post("/register", response_model=UserResponse)
def register_route(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


# -------- LOGIN --------
@router.post("/login", response_model=LoginResponse)
def login_route(data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, data)


# -------- VERIFY TOKEN (Optional Debug) --------
@router.get("/verify", response_model=MessageResponse)
def verify_token_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Token is valid ✅ for user {current_user['user_id']}"}


# -------- LOGOUT --------
@router.post("/logout", response_model=MessageResponse)
def logout_route(
    credentials=Depends(security), current_user: dict = Depends(get_current_user)
):
    token = credentials.credentials
    return logout_user(token, current_user["user_id"])
