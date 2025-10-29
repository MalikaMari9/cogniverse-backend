# ===============================
# app/controllers/system_log_controller.py — Final Unified Version
# ===============================

from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import cast, String, or_
from math import ceil
from app.db.models.system_log_model import SystemLog
from app.db.models.user_model import User
from app.db.schemas.system_log_schema import SystemLogCreate, SystemLogResponse
from app.services.utils.config_helper import get_int_config


# ============================================================
# 🔹 Get All Logs (Paginated, Searchable)
# ============================================================
def get_all_logs_paginated(
    db: Session,
    page: int = 1,
    limit: int | None = None,
    q: str | None = None,
):
    """
    Return paginated system logs with optional search by username, action_type, or details.
    """
    if limit is None:
        limit = get_int_config(db, "LogPaginationLimit", 50)

    # Base query
    query = db.query(SystemLog).join(User, isouter=True)

    # 🔍 Keyword search
    if q:
        q_like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                cast(SystemLog.action_type, String).ilike(q_like),
                cast(SystemLog.details, String).ilike(q_like),
                cast(User.username, String).ilike(q_like),
                cast(SystemLog.status, String).ilike(q_like),
            )
        )

    # 🕓 Order by newest first
    query = query.order_by(SystemLog.logid.desc())

    # Pagination
    total = query.count()
    logs = query.offset((page - 1) * limit).limit(limit).all()

    # 🧩 Add username field
    for log in logs:
        log.username = log.user.username if log.user else "System"

    return {
        "items": [SystemLogResponse.model_validate(l) for l in logs],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 1,
    }


# ============================================================
# 🔹 Get All Logs (No Pagination)
# ============================================================
def get_all_logs(db: Session):
    logs = db.query(SystemLog).join(User, isouter=True).order_by(SystemLog.logid.desc()).all()

    for log in logs:
        log.username = log.user.username if log.user else "System"
    return logs


# ============================================================
# 🔹 Get Single Log by ID
# ============================================================
def get_log_by_id(db: Session, log_id: int):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")

    log.username = log.user.username if log.user else "System"
    return log


# ============================================================
# 🔹 Create New Log
# ============================================================
def create_log(db: Session, log_data: SystemLogCreate):
    new_log = SystemLog(**log_data.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    new_log.username = new_log.user.username if new_log.user else "System"
    return new_log


# ============================================================
# 🔹 Delete Single Log
# ============================================================
def delete_log(db: Session, log_id: int):
    log = db.query(SystemLog).filter(SystemLog.logid == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="System log not found")

    db.delete(log)
    db.commit()
    return {"message": f"System log #{log_id} deleted successfully."}


# ============================================================
# 🔹 Bulk Delete Logs
# ============================================================
def delete_logs_bulk(db: Session, log_ids: list[int]):
    if not log_ids:
        raise HTTPException(status_code=400, detail="No log IDs provided.")

    logs = db.query(SystemLog).filter(SystemLog.logid.in_(log_ids)).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No matching logs found.")

    count = len(logs)
    for log in logs:
        db.delete(log)

    db.commit()
    return {"message": f"{count} system logs deleted successfully."}
