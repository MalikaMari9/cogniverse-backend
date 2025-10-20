# app/controllers/maintenance_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models.maintenance_model import Maintenance
from app.db.schemas.maintenance_schema import MaintenanceUpdate

def get_all_maintenance(db: Session):
    return db.query(Maintenance).order_by(Maintenance.maintenanceid).all()

def get_maintenance_by_key(db: Session, module_key: str):
    record = db.query(Maintenance).filter(Maintenance.module_key == module_key).first()
    if not record:
        raise HTTPException(status_code=404, detail="Module not found")
    return record

def update_maintenance(db: Session, module_key: str, data: MaintenanceUpdate, user_id: int):
    record = db.query(Maintenance).filter(Maintenance.module_key == module_key).first()
    if not record:
        raise HTTPException(status_code=404, detail="Module not found")

    if data.under_maintenance is not None:
        record.under_maintenance = data.under_maintenance
    if data.message is not None:
        record.message = data.message

    record.updated_by = user_id
    db.commit()
    db.refresh(record)
    return record
