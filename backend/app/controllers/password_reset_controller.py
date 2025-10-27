from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.services.logging_service import system_logger
from app.services.utils.config_helper import get_config_value, get_int_config, get_bool_config
import smtplib, ssl, os
from email.mime.text import MIMEText

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
RESET_TOKEN_EXPIRE_MINUTES = 30

# ────────────────────────────────────────────────
# 🔹 Token helpers
# ────────────────────────────────────────────────
def create_reset_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
        "purpose": "password_reset"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> str:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token purpose")
        return decoded["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset link expired")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted token")

# ────────────────────────────────────────────────
# 🔹 Email helper
# ────────────────────────────────────────────────
def send_reset_email(db: Session, to_email: str, reset_link: str):
    smtp_host = get_config_value(db, "smtpHost", "smtp.gmail.com")
    smtp_port = get_int_config(db, "smtpPort", 465)
    from_email = get_config_value(db, "fromEmail", os.getenv("FROM_EMAIL"))
    email_password = get_config_value(db, "emailPassword", os.getenv("EMAIL_PASSWORD"))

    use_test_override = get_bool_config(db, "useTestEmailOverride", False)
    to_email_override = get_config_value(db, "toEmail", None) if use_test_override else None
    actual_recipient = to_email_override or to_email

    msg = MIMEText(_build_email_html(reset_link), "html")
    msg["Subject"] = "🔐 Reset your CogniVerse password"
    msg["From"] = f"CogniVerse <{from_email}>"
    msg["To"] = actual_recipient

    try:
        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(from_email, email_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(from_email, email_password)
                server.send_message(msg)
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        system_logger.log_action_sync(db, action_type="EMAIL_SEND_ERROR",
                                      user_id=None, details=str(e), status="failed")

def _build_email_html(reset_link: str) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>CogniVerse Password Reset</h2>
        <p>Click below to reset your password:</p>
        <p><a href="{reset_link}">Reset My Password</a></p>
        <p>This link expires in 30 minutes.</p>
      </body>
    </html>
    """
