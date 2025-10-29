# app/controllers/payment_controller.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.credit_model import CreditConfig, CreditTransaction, Billing
from app.db.models.credit_model import CreditType
from app.services.stripe_service import create_checkout_session
from datetime import datetime
import stripe
import os

# ✅ Create a new checkout session and pending transaction
def create_payment_session(db: Session, user, pack_key: str, domain: str):
    print("🚀 [CONTROLLER] create_payment_session() triggered")
    pack = db.query(CreditConfig).filter(CreditConfig.config_key == pack_key).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Credit pack not found")

    value = pack.config_value
    stripe_price_id = value.get("stripe_price_id")
    credits = value.get("credits")
    price_usd = value.get("base_price_usd")

    success_url = f"{domain}/credit/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{domain}/credit/cancel"

    session = create_checkout_session(
    stripe_price_id, user.email, success_url, cancel_url
)

    print("🧩 Debug user:", type(user), getattr(user, "email", None), getattr(user, "userid", None))

    # Create a pending transaction
    txn = CreditTransaction(
        userid=user.userid,
        amount=credits,
        credit_type=CreditType.paid,
        reason="Credit purchase",
        packid=pack_key,
        amount_paid_usd=price_usd,
        stripe_session_id=session.id,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {"checkout_url": session.url, "session_id": session.id}


# ✅ Handle Stripe webhook
# ✅ Handle Stripe webhook
def handle_webhook_event(db: Session, event):
    if event["type"] != "checkout.session.completed":
        return {"detail": "Event ignored"}

    session = event["data"]["object"]
    stripe_session_id = session["id"]
    payment_intent = session["payment_intent"]
    email = session.get("customer_email")

    txn = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.stripe_session_id == stripe_session_id)
        .first()
    )
    if not txn:
        return {"detail": "Transaction not found"}

    # ✅ Update transaction
    txn.status = "success"  # ✅ match DB allowed value
    txn.stripe_payment_intent_id = payment_intent

    # ✅ Update billing credits
    billing = db.query(Billing).filter(Billing.userid == txn.userid).first()
    if billing:
        billing.paid_credits += txn.amount
    else:
        raise HTTPException(status_code=404, detail="Billing record not found")

    db.commit()
    return {"detail": f"Credits added: {txn.amount}"}


# ✅ Verify Stripe session after redirect
def verify_payment_session(db: Session, session_id: str):
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Stripe session retrieval failed: {str(e)}")

    if session.payment_status != "paid":
        return {"status": "pending", "detail": "Payment not completed yet."}

    txn = db.query(CreditTransaction).filter(
        CreditTransaction.stripe_session_id == session.id
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # ✅ Only update if not already success
    if txn.status != "success":
        txn.status = "success"  # ✅ use DB-consistent value
        billing = db.query(Billing).filter(Billing.userid == txn.userid).first()
        if billing:
            billing.paid_credits += txn.amount
        db.commit()

    return {"status": "success", "credits_added": txn.amount}
