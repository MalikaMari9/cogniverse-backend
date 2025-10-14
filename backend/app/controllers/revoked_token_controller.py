from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.revoked_token_model import RevokedToken
from app.db.schemas.revoked_token_schema import RevokedTokenCreate

def get_all_revoked_tokens(db: Session):
    return db.query(RevokedToken).all()

def get_revoked_token_by_id(token_id: int, db: Session):
    t = db.query(RevokedToken).filter(RevokedToken.id == token_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Revoked token not found")
    return t

def create_revoked_token(token_data: RevokedTokenCreate, db: Session):
    new_t = RevokedToken(**token_data.model_dump())
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return new_t

def delete_revoked_token(token_id: int, db: Session):
    t = db.query(RevokedToken).filter(RevokedToken.id == token_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Revoked token not found")

    db.delete(t)
    db.commit()
    return {"detail": "Revoked token deleted successfully"}
