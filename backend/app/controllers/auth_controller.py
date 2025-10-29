from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.services.jwt_service import create_access_token, create_refresh_token, revoke_token, verify_refresh_token
from app.services.utils.auth_utils import hash_password, verify_password
from app.db.schemas.user_schema import UserCreate, UserLogin
from app.services.utils.config_helper import get_int_config

# -------------------------------------------
# REGISTER USER
# -------------------------------------------
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

    # 🪙 Automatically create billing wallet
    try:
        from app.controllers import billing_controller
        from app.db.schemas.billing_schema import BillingCreate
        from app.services.utils.config_helper import get_int_config

        # Get default free credits from config_tbl (fallback to 5)
        daily_free = get_int_config(db, "dailyFreeCredits", 5)

        billing_data = BillingCreate(
            userid=new_user.userid,
            free_credits=daily_free,
            paid_credits=0
        )
        billing_controller.create_billing_record(db, billing_data)

    except Exception as e:
        # Do not block signup if billing creation fails — just log it
        print(f"⚠️ Billing wallet creation failed for user {new_user.userid}: {e}")

    return new_user


# -------------------------------------------
# LOGIN USER
# -------------------------------------------
def login_user(db: Session, data: UserLogin):
    # 🔍 Find user by email or username
    user = (
        db.query(User)
        .filter((User.email.ilike(data.identifier)) | (User.username == data.identifier))
        .first()
    )

    # 🚫 User not found
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚫 Wrong password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 🪙 Ensure billing wallet exists
    from app.db.models.credit_model import Billing
    from app.controllers import billing_controller
    from app.db.schemas.billing_schema import BillingCreate
    from app.services.utils.config_helper import get_int_config
    from datetime import datetime, timezone

    billing = db.query(Billing).filter(Billing.userid == user.userid).first()
    if not billing:
        print(f"⚠️ No billing found for user {user.userid}, creating one...")
        daily_free = get_int_config(db, "dailyFreeCredits", 5)
        billing_data = BillingCreate(
            userid=user.userid,
            free_credits=daily_free,
            paid_credits=0
        )
        billing = billing_controller.create_billing_record(db, billing_data)

    # ✅ Refresh free credits if outdated
    try:
        today_utc = datetime.now(timezone.utc).date()
        daily_free = get_int_config(db, "dailyFreeCredits", 5)

        if not billing.last_free_credit_date or billing.last_free_credit_date < today_utc:
            billing.free_credits = daily_free
            billing.last_free_credit_date = today_utc
            db.commit()
            db.refresh(billing)
            print(f"✅ Refreshed free credits for user {user.userid} on login")

    except Exception as e:
        print(f"⚠️ Failed to refresh credits for user {user.userid}: {e}")

    # 🎟️ Generate tokens
    access_token = create_access_token({"user_id": user.userid, "role": user.role}, db=db)
    refresh_token = create_refresh_token({"user_id": user.userid, "role": user.role}, db=db)

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


# -------------------------------------------
# REFRESH ACCESS TOKEN
# -------------------------------------------



def refresh_access_token(db: Session, refresh_token: str):
    """
    Validate a refresh token and issue a new access token.
    Dynamically respects config_tbl values for expiry durations.
    """
    try:
        # ✅ Verify refresh token validity (decode + check revocation)
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # ✅ Ensure user still exists
        user = db.query(User).filter(User.userid == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Get access token lifetime dynamically
        expiry_minutes = get_int_config(db, "accessTokenExpiryMinutes", 15)

        # ✅ Issue a new short-lived access token
        new_access_token = create_access_token(
            {"user_id": user.userid, "role": user.role}, db=db
        )

        return {
            "message": "Access token refreshed successfully",
            "access_token": new_access_token,
            "expires_in": expiry_minutes * 60,  # seconds
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired refresh token: {e}")
