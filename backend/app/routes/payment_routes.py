# app/routes/payment_routes.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.controllers import payment_controller
from app.services.stripe_service import verify_webhook_signature
from app.services.jwt_service import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

# 🔹 Create Stripe Checkout Session
@router.post("/create-session")
async def create_checkout_session(
    request: Request,
    pack: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    print("📨 [ROUTE] /payments/create-session called")
    print("🧾 Received pack:", pack)
    print("👤 Current user from Depends:", current_user)
    domain = request.headers.get("origin", "http://localhost:5173")
    result = payment_controller.create_payment_session(db, current_user, pack["pack_key"], domain)
    print("✅ [ROUTE] Returning result from controller:", result)
    return result


# 🔹 Stripe Webhook Receiver
@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    import stripe, os

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}

    return payment_controller.handle_webhook_event(db, event)

@router.get("/verify-session/{session_id}")
async def verify_session(session_id: str, db: Session = Depends(get_db)):
    """
    Called by frontend after successful Stripe checkout.
    Verifies session status and updates user credits if not already done.
    """
    return payment_controller.verify_payment_session(db, session_id)