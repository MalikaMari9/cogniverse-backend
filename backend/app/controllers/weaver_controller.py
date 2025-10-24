# ===============================
# app/controllers/weaver_controller.py — Soft Delete Ready
# ===============================

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.weaver_model import Weaver
from app.db.schemas.weaver_schema import WeaverCreate, WeaverUpdate


# ============================================================
# 🔹 CREATE WEAVER
# ============================================================
def create_weaver(db: Session, data: WeaverCreate):
    """Create a new weaver record."""
    try:
        new_weaver = Weaver(
            weavercontent=data.weavercontent,
            agentid=data.agentid,
            projectid=data.projectid,
        )
        db.add(new_weaver)
        db.commit()
        db.refresh(new_weaver)
        return new_weaver
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 GET WEAVER BY ID
# ============================================================
def get_weaver_by_id(db: Session, weaverid: int, include_deleted: bool = False):
    """Retrieve a single weaver record by ID."""
    weaver = db.query(Weaver).filter(Weaver.weaverid == weaverid).first()
    if not weaver or (weaver.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Weaver not found or deleted")
    return weaver


# ============================================================
# 🔹 LIST WEAVERS BY PROJECT
# ============================================================
def list_weavers_by_project(db: Session, projectid: int, include_deleted: bool = False):
    """List all weavers under a project."""
    query = db.query(Weaver).filter(Weaver.projectid == projectid)
    if not include_deleted:
        query = query.filter(Weaver.is_deleted == False)
    return query.order_by(Weaver.created_at.desc()).all()


# ============================================================
# 🔹 LIST WEAVERS BY AGENT
# ============================================================
def list_weavers_by_agent(db: Session, agentid: int, include_deleted: bool = False):
    """List all weavers linked to an agent."""
    query = db.query(Weaver).filter(Weaver.agentid == agentid)
    if not include_deleted:
        query = query.filter(Weaver.is_deleted == False)
    return query.order_by(Weaver.created_at.desc()).all()


# ============================================================
# 🔹 UPDATE WEAVER
# ============================================================
def update_weaver(db: Session, weaverid: int, data: WeaverUpdate):
    """Update an existing weaver record."""
    weaver = db.query(Weaver).filter(Weaver.weaverid == weaverid).first()
    if not weaver:
        raise HTTPException(status_code=404, detail="Weaver not found")

    if weaver.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted weaver")

    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(weaver, key, value)

    db.commit()
    db.refresh(weaver)
    return weaver


# ============================================================
# 🔹 SOFT DELETE WEAVER
# ============================================================
def delete_weaver(db: Session, weaverid: int):
    """Soft delete a weaver instead of removing it permanently."""
    weaver = db.query(Weaver).filter(Weaver.weaverid == weaverid).first()
    if not weaver:
        raise HTTPException(status_code=404, detail="Weaver not found")

    if weaver.is_deleted:
        raise HTTPException(status_code=400, detail="Weaver already deleted")

    weaver.is_deleted = True
    weaver.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Weaver {weaverid} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE WEAVER (Admin Only)
# ============================================================
def hard_delete_weaver(db: Session, weaverid: int):
    """Permanently delete a weaver record (admin cleanup only)."""
    weaver = db.query(Weaver).filter(Weaver.weaverid == weaverid).first()
    if not weaver:
        raise HTTPException(status_code=404, detail="Weaver not found")

    db.delete(weaver)
    db.commit()
    return {"detail": f"Weaver {weaverid} permanently deleted"}
