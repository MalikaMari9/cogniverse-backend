from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers.auth_controller import register_user, login_user, logout_user, refresh_access_token
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
    return {"message": f"Token is valid ✅ for user {current_user.userid}"}



# -------- LOGOUT --------
@router.post("/logout", response_model=MessageResponse)
def logout_route(
    credentials=Depends(security), current_user: dict = Depends(get_current_user)
):
    token = credentials.credentials
    return logout_user(token, current_user.userid)


# ---------------- Refresh ----------------
@router.post("/refresh", response_model=LoginResponse)
def refresh(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization", "")
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Missing or invalid Authorization header")

    refresh_token = token.replace("Bearer ", "")
    return refresh_access_token(db, refresh_token)
