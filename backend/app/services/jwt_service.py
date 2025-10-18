# app/services/jwt_service.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import engine, get_db
from app.db.models.user_model import User

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()  # looks for Authorization: Bearer <token>

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})

    # Always set sub
    if "userid" in data:
        to_encode["sub"] = str(data["userid"])
    elif "user_id" in data:
        to_encode["sub"] = str(data["user_id"])
    else:
        raise ValueError("Missing user id for JWT")
    
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(data: dict):
    """
    Create a JWT refresh token with 'exp' claim.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def verify_token(token: str):
    """
    Decode the token and check if it's revoked.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Check if token is revoked
        from app.services.jwt_service import is_token_revoked
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Get the currently authenticated user from the JWT.
    """
    token = credentials.credentials
    payload = verify_token(token)

    # The user id is in 'sub'
    userid = payload.get("sub")
    if not userid:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.userid == int(userid)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def revoke_token(token: str, userid: int):
    """
    Save a revoked token to the database.
    """
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO revoked_token_tbl (token, user_id)
                VALUES (:token, :user_id)
            """),
            {"token": token, "user_id": userid},
        )

def is_token_revoked(token: str) -> bool:
    """
    Check if a token exists in the revoked_token_tbl.
    """
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT 1 FROM revoked_token_tbl WHERE token = :token"),
            {"token": token},
        ).fetchone()
        return bool(result)


def verify_refresh_token(token: str):
    """Validate a refresh token and ensure it’s not revoked."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Check if token expired or revoked
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
