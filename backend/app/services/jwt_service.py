#app.services.jwt_service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.db.database import engine
from sqlalchemy import text
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models.user_model import User

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()  # looks for Authorization: Bearer <token>

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Check if revoked
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
    token = credentials.credentials
    payload = verify_token(token)

    # The user id is in 'sub', not 'user_id'
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.userid == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def revoke_token(token: str, user_id: int):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO revoked_token_tbl (token, user_id)
                VALUES (:token, :user_id)
            """),
            {"token": token, "user_id": user_id},
        )

def is_token_revoked(token: str) -> bool:
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT 1 FROM revoked_token_tbl WHERE token = :token"),
            {"token": token},
        ).fetchone()
        return bool(result)
