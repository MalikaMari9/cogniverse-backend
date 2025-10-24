from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.db.models.contact_model import Contact
from app.db.schemas.contact_schema import ContactCreate, ContactUpdate


# ============================================================
# 🔹 GET ALL CONTACTS
# ============================================================
def get_all_contacts(db: Session, include_deleted: bool = False):
    """Retrieve all contacts (exclude soft-deleted by default)."""
    query = db.query(Contact)
    if not include_deleted:
        query = query.filter(Contact.is_deleted == False)

    return query.order_by(Contact.created_at.desc()).all()


# ============================================================
# 🔹 GET SINGLE CONTACT
# ============================================================
def get_contact_by_id(contact_id: int, db: Session, include_deleted: bool = False):
    """Retrieve a single contact by ID."""
    contact = (
        db.query(Contact)
        .filter(Contact.contactid == contact_id)
        .first()
    )

    if not contact or (contact.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Contact not found or deleted")

    return contact


# ============================================================
# 🔹 CREATE CONTACT
# ============================================================
def create_contact(contact_data: ContactCreate, db: Session):
    """Create a new contact entry."""
    try:
        new_contact = Contact(**contact_data.model_dump())
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ============================================================
# 🔹 UPDATE CONTACT
# ============================================================
def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session):
    """Update an existing contact entry."""
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted contact")

    update_fields = contact_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


# ============================================================
# 🔹 SOFT DELETE CONTACT
# ============================================================
def delete_contact(contact_id: int, db: Session):
    """Soft delete a contact instead of removing it permanently."""
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.is_deleted:
        raise HTTPException(status_code=400, detail="Contact already deleted")

    contact.is_deleted = True
    contact.deleted_at = datetime.utcnow()

    db.commit()
    return {"detail": f"Contact {contact_id} soft-deleted successfully"}


# ============================================================
# 🔹 HARD DELETE CONTACT (Admin Only)
# ============================================================
def hard_delete_contact(contact_id: int, db: Session):
    """Permanently delete a contact (admin cleanup only)."""
    contact = db.query(Contact).filter(Contact.contactid == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"detail": f"Contact {contact_id} permanently deleted"}
