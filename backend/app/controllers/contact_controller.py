from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.contact_model import Contact
from app.db.schemas.contact_schema import ContactCreate, ContactUpdate


def get_all_contacts(db: Session):
    return db.query(Contact).all()


def get_contact_by_id(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


def create_contact(contact_data: ContactCreate, db: Session):
    new_contact = Contact(**contact_data.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session):
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"detail": "Contact deleted successfully"}
