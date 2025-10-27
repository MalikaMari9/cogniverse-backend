from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user_model import User
from app.services.jwt_service import create_access_token
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
import smtplib
from email.mime.text import MIMEText
import os

router = APIRouter(prefix="/auth", tags=["Forgot Password"])

SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret")
ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 30

# -------------------- Schemas --------------------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# -------------------- Helpers --------------------
def create_reset_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        "purpose": "password_reset"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token purpose")
        return decoded["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset link expired")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted token")

def send_reset_email(to_email: str, reset_link: str):
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222; background: #f9fafb; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); padding: 30px;">
          <h2 style="color: #4a90e2; text-align: center;">CogniVerse Password Reset</h2>
          <p>Hello,</p>
          <p>We received a request to reset your password. Click the button below to set a new one:</p>
          <p style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background: #4a90e2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; display: inline-block;">
              Reset My Password
            </a>
          </p>
          <p>If the button doesn’t work, you can also copy and paste this link into your browser:</p>
          <p style="word-break: break-all; color: #555;">{reset_link}</p>
          <p style="font-size: 13px; color: #888;">This link will expire in 30 minutes.</p>
          <p style="font-size: 13px; color: #888;">If you didn’t request this reset, you can safely ignore this email.</p>
          <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
          <p style="font-size: 12px; text-align: center; color: #aaa;">© {datetime.utcnow().year} CogniVerse. All rights reserved.</p>
        </div>
      </body>
    </html>
    """

    msg = MIMEText(html, "html")
    msg["Subject"] = "🔐 Reset your CogniVerse password"
    msg["From"] = "no-reply@cogniverse.ai"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("phyusinthantygn2004@gmail.com", "qjei cosm yvhm tmqr")
        server.send_message(msg)


# -------------------- Routes --------------------
@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(data.email)
    reset_link = f"http://localhost:5173/reset-password?token={token}"

    # Send in background
    background_tasks.add_task(send_reset_email, data.email, reset_link)

    # Log request
    if dedupe_service.should_log_action("FORGOT_PASSWORD_REQUEST", user.userid):
        await system_logger.log_action(
            db=db,
            action_type="FORGOT_PASSWORD_REQUEST",
            user_id=user.userid,
            details=f"Password reset link sent to {data.email}",
            request=request,
            status="active"
        )

    return {"message": "Password reset link sent to your email."}


@router.post("/reset-password")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    email = verify_reset_token(data.token)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password (ensure hashing consistent with your auth controller)
    from app.services.utils.auth_utils import hash_password
    user.password_hash = hash_password(data.new_password)
    db.commit()

    # Log reset
    if dedupe_service.should_log_action("PASSWORD_RESET", user.userid):
        await system_logger.log_action(
            db=db,
            action_type="PASSWORD_RESET",
            user_id=user.userid,
            details=f"Password reset successful for {user.email}",
            request=request,
            status="active"
        )

    return {"message": "Password has been reset successfully."}
