from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.contact_schema import ContactCreate, ContactUpdate, ContactResponse
from app.controllers import contact_controller
from app.db.database import get_db

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/", response_model=List[ContactResponse])
def get_all_contacts(db: Session = Depends(get_db)):
    return contact_controller.get_all_contacts(db)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    return contact_controller.get_contact_by_id(contact_id, db)


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return contact_controller.create_contact(contact, db)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    return contact_controller.update_contact(contact_id, contact, db)


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    return contact_controller.delete_contact(contact_id, db)
