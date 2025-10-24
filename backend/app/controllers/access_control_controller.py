from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.access_control_model import AccessControl
from app.db.schemas.access_control_schema import (
    AccessControlCreate, AccessControlUpdate,
    LifecycleStatus, AccessLevel
)

# ============================================================
# 🔹 Get all (excluding soft-deleted)
# ============================================================
def get_all_access_controls(db: Session):
    return (
        db.query(AccessControl)
        .filter(AccessControl.is_deleted == False)
        .all()
    )

# ============================================================
# 🔹 Get by ID (must not be deleted)
# ============================================================
def get_access_by_id(access_id: int, db: Session):
    a = (
        db.query(AccessControl)
        .filter(AccessControl.accessid == access_id, AccessControl.is_deleted == False)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="Access control record not found or deleted")
    return a

# ============================================================
# 🔹 Create
# ============================================================
def create_access_control(access_data: AccessControlCreate, db: Session):
    existing = (
        db.query(AccessControl)
        .filter(AccessControl.module_key == access_data.module_key)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Module key already exists")

    new_a = AccessControl(**access_data.model_dump())
    db.add(new_a)
    db.commit()
    db.refresh(new_a)
    return new_a

# ============================================================
# 🔹 Update
# ============================================================
def update_access_control(access_id: int, access_data: AccessControlUpdate, db: Session):
    a = (
        db.query(AccessControl)
        .filter(AccessControl.accessid == access_id, AccessControl.is_deleted == False)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="Access control record not found or deleted")

    data = access_data.model_dump(exclude_unset=True)

    enum_fields = {
        "user_access": AccessLevel,
        "admin_access": AccessLevel,
        "superadmin_access": AccessLevel,
        "status": LifecycleStatus,
    }

    for key, value in data.items():
        if key in enum_fields and isinstance(value, str):
            try:
                data[key] = enum_fields[key](value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid enum value '{value}' for {key}")

    for key, value in data.items():
        setattr(a, key, value)

    db.commit()
    db.refresh(a)
    return a

# ============================================================
# 🔹 Soft Delete (mark as deleted)
# ============================================================
def delete_access_control(access_id: int, db: Session):
    a = db.query(AccessControl).filter(AccessControl.accessid == access_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Access control record not found")

    # ✅ Instead of deleting, mark it
    a.is_deleted = True
    a.status = LifecycleStatus.archived
    db.commit()
    return {"detail": f"Access control {access_id} marked as deleted"}
