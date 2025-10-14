from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.controllers import system_log_controller
from app.db.database import get_db

router = APIRouter(prefix="/system-logs", tags=["System Logs"])


@router.get("/", response_model=List[SystemLogResponse])
def get_all_logs(db: Session = Depends(get_db)):
    return system_log_controller.get_all_logs(db)


@router.get("/{log_id}", response_model=SystemLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    return system_log_controller.get_log_by_id(log_id, db)


@router.post("/", response_model=SystemLogResponse, status_code=201)
def create_log(log: SystemLogCreate, db: Session = Depends(get_db)):
    return system_log_controller.create_log(log, db)


@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    return system_log_controller.delete_log(log_id, db)
