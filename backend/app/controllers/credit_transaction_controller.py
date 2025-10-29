# app/controllers/credit_transaction_controller.py
from math import ceil
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import cast, String
from app.db.models.credit_model import CreditTransaction
from app.db.models.user_model import User
from app.db.schemas.credit_transaction_schema import (
    CreditTransactionCreate,
    CreditTransactionUpdate,
    CreditTransactionResponse,
)
from app.services.credit_service import apply_credit_transaction
from app.services.utils.config_helper import get_int_config


# ──────────────────────────────────────────────────────────────
# 1️⃣ Create transaction
# ──────────────────────────────────────────────────────────────
def create_transaction(db: Session, tx_data: CreditTransactionCreate):
    new_tx = CreditTransaction(**tx_data.dict())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # ✅ Auto-apply to user's billing balance if already marked success
    if (new_tx.status or "").lower() in ["success", "completed"]:
        try:
            apply_credit_transaction(db, new_tx.transactionid)
        except Exception as e:
            # optional: rollback or log failure
            print(f"[Credit Sync Error] {e}")

    return new_tx
def get_all_transactions_paginated(
    db: Session,
    page: int = 1,
    limit: int | None = None,
    q: str | None = None,
    status: str | None = None,
):
    """
    Return paginated credit transactions with username.
    Supports filters: q (search), status.
    """

    if limit is None:
        limit = get_int_config(db, "LogPaginationLimit", 10)

    # start with base query + join (only once!)
    query = (
        db.query(CreditTransaction, User.username)
        .join(User, User.userid == CreditTransaction.userid, isouter=True)
        .filter(CreditTransaction.is_deleted == False)
    )

    # 🔍 Search (username, reason, packid, credit_type, status)
    if q:
        q_like = f"%{q.lower()}%"
        query = query.filter(
            (User.username.ilike(q_like))
            | (CreditTransaction.reason.ilike(q_like))
            | (CreditTransaction.packid.ilike(q_like))
            | (cast(CreditTransaction.credit_type, String).ilike(q_like))
            | (cast(CreditTransaction.status, String).ilike(q_like))
        )

    # ⚙️ Status filter
    if status and status.lower() != "all":
        query = query.filter(cast(CreditTransaction.status, String).ilike(status))

    # Count total first
    total = query.count()

    # Fetch paginated results (no need to join again)
    rows = (
        query.order_by(CreditTransaction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Build response
    items = []
    for tx, username in rows:
        tx_data = CreditTransactionResponse.model_validate(tx).model_dump()
        tx_data["username"] = username or "Unknown"
        items.append(tx_data)

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 1,
    }
# ──────────────────────────────────────────────────────────────
# 3️⃣ Get transaction by ID
# ──────────────────────────────────────────────────────────────
def get_transaction_by_id(db: Session, transaction_id: int):
    tx = (
        db.query(CreditTransaction)
        .filter(
            CreditTransaction.transactionid == transaction_id,
            CreditTransaction.is_deleted == False,
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


# ──────────────────────────────────────────────────────────────
# 4️⃣ Get transactions by user ID
# ──────────────────────────────────────────────────────────────
def get_transactions_by_userid(db: Session, userid: int):
    txs = (
        db.query(CreditTransaction)
        .filter(
            CreditTransaction.userid == userid,
            CreditTransaction.is_deleted == False,
        )
        .order_by(CreditTransaction.created_at.desc())
        .all()
    )
    return txs


# ──────────────────────────────────────────────────────────────
# 5️⃣ Update transaction
# ──────────────────────────────────────────────────────────────
def update_transaction(db: Session, transaction_id: int, update_data: CreditTransactionUpdate):
    tx = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.transactionid == transaction_id)
        .first()
    )
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
    tx = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.transactionid == transaction_id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.is_deleted = True
    db.commit()
    return {"message": f"Transaction {transaction_id} marked as deleted."}
