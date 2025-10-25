# app/services/stripe_service.py
import os
import stripe
from fastapi import HTTPException, Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
print("🔑 Loaded Stripe secret key:", "✅ SET" if stripe.api_key else "❌ MISSING")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# ✅ Create checkout session
def create_checkout_session(price_id: str, user_email: str, success_url: str, cancel_url: str):
    print("💳 [SERVICE] create_checkout_session() reached")
    print("📦 Stripe price ID:", price_id)
    try:
        session = stripe.checkout.Session.create(
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            customer_email=user_email,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        print("📦 Stripe price ID used:", price_id)

        return session
    except Exception as e:
        import traceback
        print("❌ Stripe session creation failed:")
        traceback.print_exc()
        print("🧩 Exception type:", type(e))
        print("🧩 Exception message:", str(e))
        raise HTTPException(status_code=500, detail=f"Stripe session error: {e}")

# ✅ Verify webhook signature + return event
def verify_webhook_signature(request: Request):
    payload = request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
