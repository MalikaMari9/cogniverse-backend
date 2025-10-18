from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.services.jwt_service import create_access_token, create_refresh_token, revoke_token, verify_refresh_token
from app.services.utils.auth_utils import hash_password, verify_password
from app.db.schemas.user_schema import UserCreate, UserLogin


# -------------------------------------------
# REGISTER USER
# -------------------------------------------
def register_user(db: Session, data: UserCreate):
    # Check duplicates
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash password
    hashed_pw = hash_password(data.password)

    # Create new user
    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hashed_pw,
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------------------------
# LOGIN USER
# -------------------------------------------
def login_user(db: Session, data: UserLogin):
    # Find user by email or username
    user = (
        db.query(User)
        .filter((User.email.ilike(data.identifier)) | (User.username == data.identifier))
        .first()
    )

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"user_id": user.userid, "role": user.role})
    refresh_token = create_refresh_token({"user_id": user.userid, "role": user.role})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# -------------------------------------------
# LOGOUT USER
# -------------------------------------------
def logout_user(token: str, user_id: int):
    try:
        revoke_token(token, user_id)
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------
# REFRESH ACCESS TOKEN
# -------------------------------------------


def refresh_access_token(db: Session, refresh_token: str):
    """
    Validate a refresh token and issue a new access token.
    Future scalability:
      - Can be extended with session_tbl for per-device refresh management.
      - Can track refresh usage timestamps for analytics or limits.
    """
    try:
        # Verify refresh token validity
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # Ensure user still exists
        user = db.query(User).filter(User.userid == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Issue a new short-lived access token
        new_access_token = create_access_token({"user_id": user.userid, "role": user.role})

        return {
            "message": "Access token refreshed successfully",
            "access_token": new_access_token,
            "expires_in": 15 * 60,  # seconds (15 minutes)
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired refresh token: {e}")
