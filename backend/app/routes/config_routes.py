from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.config_schema import ConfigCreate, ConfigUpdate, ConfigResponse
from app.controllers import config_controller
from app.db.database import get_db

router = APIRouter(prefix="/configs", tags=["Configs"])

@router.get("/", response_model=List[ConfigResponse])
def get_all_configs(db: Session = Depends(get_db)):
    return config_controller.get_all_configs(db)

@router.get("/{config_id}", response_model=ConfigResponse)
def get_config(config_id: int, db: Session = Depends(get_db)):
    return config_controller.get_config_by_id(config_id, db)

@router.post("/", response_model=ConfigResponse, status_code=201)
def create_config(config: ConfigCreate, db: Session = Depends(get_db)):
    return config_controller.create_config(config, db)

@router.put("/{config_id}", response_model=ConfigResponse)
def update_config(config_id: int, config: ConfigUpdate, db: Session = Depends(get_db)):
    return config_controller.update_config(config_id, config, db)

@router.delete("/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    return config_controller.delete_config(config_id, db)
