from fastapi import APIRouter, Depends, Request, HTTPException
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
from app.db.models.user_model import User
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service  # Import the deduplication service

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -------- REGISTER --------
@router.post("/register", response_model=UserResponse)
async def register_route(
    request: Request,
    data: UserCreate, 
    db: Session = Depends(get_db)
):
    try:
        result = register_user(db, data)
        
        # Log successful registration with deduplication
        if dedupe_service.should_log_action("USER_REGISTRATION", result.userid):
            await system_logger.log_action(
                db=db,
                action_type="USER_REGISTRATION",
                user_id=result.userid,
                details=f"New user registered: {result.username} ({result.email})",
                request=request,
                status="active"
            )
        print("am here")    
        
        return result
        
    except HTTPException as e:
        # Log failed registration attempt (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="REGISTRATION_FAILED",
            user_id=None,
            details=f"Registration failed for {data.email}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        # Log unexpected registration error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="REGISTRATION_ERROR",
            user_id=None,
            details=f"Registration error for {data.email}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# -------- LOGIN --------
@router.post("/login", response_model=LoginResponse)
async def login_route(
    request: Request,
    data: UserLogin, 
    db: Session = Depends(get_db)
):
    try:
        result = login_user(db, data)
        
        # Log successful login by extracting user_id from token
        try:
            # Decode the token to get user_id without database query
            import jwt
            token = result["access_token"]
            # Decode without verification just to get the payload
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("user_id")
            
            if user_id:
                # Get username for the log (optional)
                user = db.query(User).filter(User.userid == user_id).first()
                username = user.username if user else "Unknown"
                
                # Use deduplication for login success
                if dedupe_service.should_log_action("LOGIN_SUCCESS", user_id):
                    await system_logger.log_action(
                        db=db,
                        action_type="LOGIN_SUCCESS",
                        user_id=user_id,
                        details=f"User logged in successfully: {username}",
                        request=request,
                        status="active"
                    )
                    print(f"✅ Login success logged for user_id: {user_id}")
                
        except Exception as log_error:
            print(f"❌ Logging failed: {log_error}")
        
        return result
        
    except HTTPException as e:
        # Log failed login attempt with deduplication based on identifier
        try:
            # Use the email/identifier as a unique key for failed attempts
            unique_key = f"failed_{data.identifier}"
            if dedupe_service.should_log_action("LOGIN_FAILED", 0, unique_key):  # Use 0 as user_id for failed attempts
                await system_logger.log_action(
                    db=db,
                    action_type="LOGIN_FAILED", 
                    user_id=None,
                    details=f"Login failed for {data.identifier}: {e.detail}",
                    request=request,
                    status="active"
                )
                print("✅ Login failure logged")
        except Exception as log_error:
            print(f"❌ Failed login logging failed: {log_error}")
        raise e


# -------- LOGOUT --------
@router.post("/logout", response_model=MessageResponse)
async def logout_route(
    request: Request,
    credentials=Depends(security), 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        result = logout_user(token, current_user.userid)
        
        # Log successful logout with deduplication
        if dedupe_service.should_log_action("LOGOUT", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="LOGOUT",
                user_id=current_user.userid,
                details="User logged out successfully",
                request=request,
                status="active"
            )
        
        return result
        
    except Exception as e:
        # Log logout error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="LOGOUT_ERROR",
            user_id=current_user.userid,
            details=f"Logout error: {str(e)}",
            request=request,
            status="active"
        )
        raise


# ---------------- Refresh ----------------
@router.post("/refresh")
async def refresh(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Called when access token expires.
    The frontend should send Authorization: Bearer <refresh_token>
    """
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        result = refresh_access_token(db, token)
        
        # Extract user_id from the token
        try:
            import jwt
            # Decode without verification to get user_id
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("user_id")
            
            # Log token refresh with deduplication
            if user_id and dedupe_service.should_log_action("TOKEN_REFRESH", user_id):
                await system_logger.log_action(
                    db=db,
                    action_type="TOKEN_REFRESH",
                    user_id=user_id,
                    details="Access token refreshed successfully",
                    request=request,
                    status="active"
                )
                
        except Exception as decode_error:
            print(f"❌ Could not decode token for logging: {decode_error}")
        
        return result
        
    except HTTPException as e:
        # Log failed token refresh with deduplication based on IP
        try:
            client_ip = request.client.host if request.client else "unknown"
            unique_key = f"refresh_failed_{client_ip}"
            if dedupe_service.should_log_action("TOKEN_REFRESH_FAILED", 0, unique_key):
                await system_logger.log_action(
                    db=db,
                    action_type="TOKEN_REFRESH_FAILED",
                    user_id=None,
                    details=f"Token refresh failed: {e.detail}",
                    request=request,
                    status="active"
                )
        except Exception as log_error:
            print(f"❌ Failed refresh logging failed: {log_error}")
        raise e
    except Exception as e:
        # Log token refresh error (no deduplication for errors)
        await system_logger.log_action(
            db=db,
            action_type="TOKEN_REFRESH_ERROR",
            user_id=None,
            details=f"Token refresh error: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")