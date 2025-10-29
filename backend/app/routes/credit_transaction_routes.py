from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.schemas.credit_transaction_schema import (
    CreditTransactionCreate,
    CreditTransactionUpdate,
    CreditTransactionResponse,
)
from app.controllers import credit_transaction_controller
from app.services.jwt_service import get_current_user
from app.services.utils.permissions_helper import enforce_permission_auto

router = APIRouter(prefix="/credit-transactions", tags=["Credit Transactions"])


# ──────────────────────────────────────────────────────────────
# Create new transaction
# ──────────────────────────────────────────────────────────────
@router.post("/", response_model=CreditTransactionResponse)
def create_transaction(
    tx: CreditTransactionCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    return credit_transaction_controller.create_transaction(db, tx)


from fastapi import Query

@router.get("/", response_model=dict)
def get_all_transactions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int | None = Query(None, ge=1, le=100),
    q: str | None = Query(None, description="Search keyword"),
    status: str | None = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    result = credit_transaction_controller.get_all_transactions_paginated(
        db, page=page, limit=limit, q=q, status=status
    )
    return result

# ──────────────────────────────────────────────────────────────
# Get transaction by ID
# ──────────────────────────────────────────────────────────────
@router.get("/{transaction_id}", response_model=CreditTransactionResponse)
def get_transaction_by_id(
    transaction_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    return credit_transaction_controller.get_transaction_by_id(db, transaction_id)


# ──────────────────────────────────────────────────────────────
# Get transactions by user
# ──────────────────────────────────────────────────────────────
@router.get("/user/{userid}", response_model=List[CreditTransactionResponse])
def get_transactions_by_userid(
    userid: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    return credit_transaction_controller.get_transactions_by_userid(db, userid)


# ──────────────────────────────────────────────────────────────
# Update transaction
# ──────────────────────────────────────────────────────────────
@router.put("/{transaction_id}", response_model=CreditTransactionResponse)
def update_transaction(
    transaction_id: int,
    tx_update: CreditTransactionUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    return credit_transaction_controller.update_transaction(db, transaction_id, tx_update)


# ──────────────────────────────────────────────────────────────
# Soft delete transaction
# ──────────────────────────────────────────────────────────────
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_permission_auto(db, current_user, "CREDIT_TRANSACTIONS", request)
    return credit_transaction_controller.delete_transaction(db, transaction_id)
