from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.schemas.maintenance_schema import MaintenanceResponse, MaintenanceUpdate
from app.controllers import maintenance_controller as controller
from app.services.jwt_service import get_current_user
from app.db.models.maintenance_model import Maintenance
from sqlalchemy import func
router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@router.get("/", response_model=List[MaintenanceResponse])
def get_all_maintenance(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return controller.get_all_maintenance(db)

# 👇 alias route: handles /maintenance (no slash)
@router.get("", include_in_schema=False)
def get_all_maintenance_alias(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return get_all_maintenance(db, current_user)

@router.put("/{module_key}", response_model=MaintenanceResponse)
def update_maintenance(module_key: str, data: MaintenanceUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return controller.update_maintenance(db, module_key, data, current_user.userid)

# backend/app/routes/maintenance_routes.py
@router.get("/{module_key}")
def get_module_maintenance(module_key: str, db: Session = Depends(get_db)):
    entry = db.query(Maintenance).filter(Maintenance.module_key.ilike(module_key)).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"No maintenance entry for {module_key}")
    return {
        "module_key": entry.module_key,
        "under_maintenance": entry.under_maintenance,
        "message": entry.message,
        "updated_at": entry.updated_at
    }


# backend/app/routes/maintenance_routes.py
@router.get("/global")
def get_global_maintenance(db: Session = Depends(get_db)):
    global_entry = (
    db.query(Maintenance)
    .filter(func.lower(Maintenance.module_key) == "global")
    .first()
)
    if not global_entry:
        raise HTTPException(status_code=404, detail="Global maintenance entry not found")
    return {
        "module_key": global_entry.module_key,
        "under_maintenance": global_entry.under_maintenance,
        "message": global_entry.message,
        "updated_at": global_entry.updated_at
    }
