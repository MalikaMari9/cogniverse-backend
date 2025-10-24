from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.credit_model import CreditConfig, LifecycleStatus
from app.db.schemas.credit_config_schema import CreditConfigCreate, CreditConfigUpdate


def get_all_credit_configs(db: Session):
    return db.query(CreditConfig).all()


def get_credit_config_by_id(creditid: int, db: Session):
    config = db.query(CreditConfig).filter(CreditConfig.creditid == creditid).first()
    if not config:
        raise HTTPException(status_code=404, detail="Credit pack not found")
    return config


def create_credit_config(data: CreditConfigCreate, db: Session):
    existing = db.query(CreditConfig).filter(CreditConfig.config_key == data.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Credit pack key already exists")

    new_pack = CreditConfig(**data.model_dump())
    db.add(new_pack)
    db.commit()
    db.refresh(new_pack)
    return new_pack


def update_credit_config(creditid: int, data, db: Session):
    pack = db.query(CreditConfig).filter(CreditConfig.creditid == creditid).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Credit pack not found")

    update_data = data.model_dump(exclude_unset=True)

    # ✅ Handle Enum safely
    if "status" in update_data and isinstance(update_data["status"], str):
        try:
            update_data["status"] = LifecycleStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status '{update_data['status']}'")

    # ✅ Skip None config_value to avoid null constraint error
    if "config_value" in update_data and update_data["config_value"] is None:
        update_data.pop("config_value")

    for key, value in update_data.items():
        setattr(pack, key, value)

    db.commit()
    db.refresh(pack)
    return pack


def delete_credit_config(creditid: int, db: Session):
    pack = db.query(CreditConfig).filter(CreditConfig.creditid == creditid).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Credit pack not found")

    db.delete(pack)
    db.commit()
    return {"detail": "Credit pack deleted successfully"}
