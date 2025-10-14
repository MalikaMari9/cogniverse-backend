from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.system_log_model import SystemLog
from app.db.schemas.system_log_schema import SystemLogCreate


def get_all_logs(db: Session):
    return db.query(SystemLog).all()


def get_log_by_id(log_id: int, db: Session):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")
    return log


def create_log(log_data: SystemLogCreate, db: Session):
    new_log = SystemLog(**log_data.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


def delete_log(log_id: int, db: Session):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")

    db.delete(log)
    db.commit()
    return {"detail": "System log deleted successfully"}
