from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.revoked_token_schema import RevokedTokenCreate, RevokedTokenResponse
from app.controllers import revoked_token_controller
from app.db.database import get_db

router = APIRouter(prefix="/revoked-tokens", tags=["Revoked Tokens"])

@router.get("/", response_model=List[RevokedTokenResponse])
def get_all_revoked_tokens(db: Session = Depends(get_db)):
    return revoked_token_controller.get_all_revoked_tokens(db)

@router.get("/{token_id}", response_model=RevokedTokenResponse)
def get_revoked_token(token_id: int, db: Session = Depends(get_db)):
    return revoked_token_controller.get_revoked_token_by_id(token_id, db)

@router.post("/", response_model=RevokedTokenResponse, status_code=201)
def create_revoked_token(token: RevokedTokenCreate, db: Session = Depends(get_db)):
    return revoked_token_controller.create_revoked_token(token, db)

@router.delete("/{token_id}")
def delete_revoked_token(token_id: int, db: Session = Depends(get_db)):
    return revoked_token_controller.delete_revoked_token(token_id, db)
