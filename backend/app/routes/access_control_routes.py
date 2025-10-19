from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.access_control_schema import (
    AccessControlCreate, AccessControlUpdate, AccessControlResponse
)
from app.controllers import access_control_controller
from app.db.database import get_db

router = APIRouter(prefix="/access-controls", tags=["Access Controls"])

@router.get("/", response_model=List[AccessControlResponse])
def get_all_access_controls(db: Session = Depends(get_db)):
    return access_control_controller.get_all_access_controls(db)

@router.get("/{access_id}", response_model=AccessControlResponse)
def get_access_control(access_id: int, db: Session = Depends(get_db)):
    return access_control_controller.get_access_by_id(access_id, db)

@router.post("/", response_model=AccessControlResponse, status_code=201)
def create_access_control(access: AccessControlCreate, db: Session = Depends(get_db)):
    return access_control_controller.create_access_control(access, db)

@router.put("/{access_id}", response_model=AccessControlResponse)
def update_access_control(access_id: int, access: AccessControlUpdate, db: Session = Depends(get_db)):
    return access_control_controller.update_access_control(access_id, access, db)

@router.delete("/{access_id}")
def delete_access_control(access_id: int, db: Session = Depends(get_db)):
    return access_control_controller.delete_access_control(access_id, db)