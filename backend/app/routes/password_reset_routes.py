from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user_model import User
from app.controllers.password_reset_controller import (
    create_reset_token, verify_reset_token, send_reset_email
)
from app.db.schemas.password_reset_schema import (
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service
from app.services.utils.config_helper import get_config_value
from app.services.utils.auth_utils import hash_password

router = APIRouter(prefix="/auth", tags=["Forgot Password"])

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
    frontend_base = get_config_value(db, "frontendBaseUrl", "http://localhost:5173")
    reset_link = f"{frontend_base.rstrip('/')}/reset-password?token={token}"

    background_tasks.add_task(send_reset_email, db, data.email, reset_link)

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
async def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    db.commit()

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
