from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.config_model import Config
from app.db.schemas.config_schema import ConfigCreate, ConfigUpdate

def get_all_configs(db: Session):
    return db.query(Config).all()

def get_config_by_id(config_id: int, db: Session):
    config = db.query(Config).filter(Config.configid == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config

def create_config(config_data: ConfigCreate, db: Session):
    existing = db.query(Config).filter(Config.config_key == config_data.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Config key already exists")

    new_config = Config(**config_data.model_dump())
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config

def update_config(config_id: int, config_data: ConfigUpdate, db: Session):
    config = db.query(Config).filter(Config.configid == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    for key, value in config_data.model_dump(exclude_unset=True).items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config

def delete_config(config_id: int, db: Session):
    config = db.query(Config).filter(Config.configid == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    db.delete(config)
    db.commit()
    return {"detail": "Config deleted successfully"}
