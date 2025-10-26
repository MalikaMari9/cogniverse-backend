from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.system_log_model import SystemLog
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.services.utils.config_helper import get_int_config
from math import ceil
def get_all_logs_paginated(db: Session, page: int = 1, limit: int | None = None):
    # 🔹 Use config if no explicit limit provided
    if limit is None:
        limit = get_int_config(db, "LogPaginationLimit", 50)

    query = db.query(SystemLog).order_by(SystemLog.logid.desc())

    total = query.count()
    start = (page - 1) * limit
    logs = query.offset(start).limit(limit).all()

    # Add username to each log
    for log in logs:
        log.username = log.user.username if log.user else "System"

    return {
        "items": [SystemLogResponse.model_validate(l) for l in logs],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 1,
    }
def get_all_logs(db: Session):
    logs = db.query(SystemLog).all()
    
    # Add username to each log
    for log in logs:
        if log.user:
            log.username = log.user.username
        else:
            log.username = "System"
    
    return logs

def get_log_by_id(log_id: int, db: Session):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")
    
    # Add username
    if log.user:
        log.username = log.user.username
    else:
        log.username = "System"
    
    return log

def create_log(log_data: SystemLogCreate, db: Session):
    new_log = SystemLog(**log_data.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    # Add username to response
    if new_log.user:
        new_log.username = new_log.user.username
    else:
        new_log.username = "System"
    
    return new_log

def delete_log(log_id: int, db: Session):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")

    db.delete(log)
    db.commit()
    return {"detail": "System log deleted successfully"}

# Add bulk delete function
def delete_logs_bulk(log_ids: list, db: Session):
    logs = db.query(SystemLog).filter(SystemLog.logid.in_(log_ids)).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found to delete")
    
    for log in logs:
        db.delete(log)
    
    db.commit()
    return {"detail": f"{len(logs)} system logs deleted successfully"}