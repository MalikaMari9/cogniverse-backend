from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.credit_model import CreditTransaction
from app.db.schemas.credit_transaction_schema import (
    CreditTransactionCreate, CreditTransactionUpdate
)
from app.services.credit_service import apply_credit_transaction

# ──────────────────────────────────────────────────────────────
# 1️⃣ Create transaction
# ──────────────────────────────────────────────────────────────
def create_transaction(db: Session, tx_data: CreditTransactionCreate):
    new_tx = CreditTransaction(**tx_data.dict())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # ✅ Auto-apply to user's billing balance if already marked success
    if new_tx.status.lower() in ["success", "completed"]:
        try:
            apply_credit_transaction(db, new_tx.transactionid)
        except Exception as e:
            # optional: rollback or log failure
            print(f"[Credit Sync Error] {e}")

    return new_tx


# ──────────────────────────────────────────────────────────────
# 2️⃣ Get all transactions
# ──────────────────────────────────────────────────────────────
def get_all_transactions(db: Session):
    return (
        db.query(CreditTransaction)
        .filter(CreditTransaction.is_deleted == False)
        .order_by(CreditTransaction.created_at.desc())
        .all()
    )


# ──────────────────────────────────────────────────────────────
# 3️⃣ Get transaction by ID
# ──────────────────────────────────────────────────────────────
def get_transaction_by_id(db: Session, transaction_id: int):
    tx = db.query(CreditTransaction).filter(
        CreditTransaction.transactionid == transaction_id,
        CreditTransaction.is_deleted == False,
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return tx


# ──────────────────────────────────────────────────────────────
# 4️⃣ Get transactions by user ID
# ──────────────────────────────────────────────────────────────
def get_transactions_by_userid(db: Session, userid: int):
    txs = db.query(CreditTransaction).filter(
        CreditTransaction.userid == userid,
        CreditTransaction.is_deleted == False,
    ).order_by(CreditTransaction.created_at.desc()).all()

    return txs


# ──────────────────────────────────────────────────────────────
# 5️⃣ Update transaction
# ──────────────────────────────────────────────────────────────
def update_transaction(db: Session, transaction_id: int, update_data: CreditTransactionUpdate):
    tx = db.query(CreditTransaction).filter(CreditTransaction.transactionid == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)
    return tx


# ──────────────────────────────────────────────────────────────
# 6️⃣ Soft delete transaction
# ──────────────────────────────────────────────────────────────
def delete_transaction(db: Session, transaction_id: int):
    tx = db.query(CreditTransaction).filter(CreditTransaction.transactionid == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.is_deleted = True
    db.commit()
    return {"message": f"Transaction {transaction_id} marked as deleted."}
