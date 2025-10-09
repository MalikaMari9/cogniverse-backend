# app/services/utils/auth_utils.py
from passlib.hash import bcrypt
from fastapi import HTTPException

def hash_password(password: str) -> str:
    try:
        return bcrypt.hash(password)
    except Exception:
        raise HTTPException(status_code=500, detail="Error hashing password")

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.verify(password, hashed)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid password")
