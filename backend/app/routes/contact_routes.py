# ===============================
# app/routes/contact_routes.py — Soft Delete Ready
# ===============================

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.schemas.contact_schema import ContactCreate, ContactUpdate, ContactResponse
from app.controllers import contact_controller
from app.db.database import get_db
from app.services.jwt_service import get_current_user
from app.services.logging_service import system_logger
from app.services.dedupe_service import dedupe_service
from app.services.utils.permissions_helper import enforce_permission_auto
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from app.controllers.contact_controller import create_contact
from app.db.schemas.contact_schema import ContactCreate
from app.db.database import get_db
from app.services.utils.contact_helper import send_email
from typing import Optional
from app.db.models.user_model import User
from app.services.jwt_service import get_current_user
from app.services.utils.contact_helper import send_contact_notification
import os
from app.services.utils.config_helper import get_config_value
router = APIRouter(prefix="/contacts", tags=["Contacts"])


# ===============================
# 🔹 Get All Contacts
# ===============================
@router.get("/", response_model=List[ContactResponse])
async def get_all_contacts(
    request: Request,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted contacts"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "CONTACTS", request)
        result = contact_controller.get_all_contacts(db, include_deleted=include_deleted)

        if dedupe_service.should_log_action("CONTACT_LIST_VIEW", current_user.userid):
            total = len(result or [])
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_LIST_VIEW",
                user_id=current_user.userid,
                details=f"Viewed contacts list (include_deleted={include_deleted}) ({total} total)",
                request=request,
                status="active"
            )

        return result

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_LIST_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing contacts list: {str(e)}",
            request=request,
            status="active"
        )
        raise


# ===============================
# 🔹 Get Single Contact
# ===============================
@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    request: Request,
    contact_id: int,
    include_deleted: Optional[bool] = Query(False, description="Include soft-deleted contact"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "CONTACTS", request)
        result = contact_controller.get_contact_by_id(contact_id, db, include_deleted=include_deleted)

        cache_key = f"contact_view_{contact_id}"
        if dedupe_service.should_log_action("CONTACT_VIEW", current_user.userid, cache_key):
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_VIEW",
                user_id=current_user.userid,
                details=f"Viewed contact ID {contact_id} (include_deleted={include_deleted})",
                request=request,
                status="active"
            )

        return result

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_VIEW_ERROR",
            user_id=current_user.userid,
            details=f"Error viewing contact ID {contact_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise


# ===============================
# 🔹 Create Contact
# ===============================
"""
@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    request: Request,
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        enforce_permission_auto(db, current_user, "CONTACTS_SEND", request)
        result = contact_controller.create_contact(contact, db)

        if dedupe_service.should_log_action("CONTACT_CREATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_CREATE",
                user_id=current_user.userid,
                details=f"Created new contact: {getattr(contact, 'name', 'Unnamed')}",
                request=request,
                status="active"
            )

        return result

    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_CREATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to create contact: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_CREATE_ERROR",
            user_id=current_user.userid,
            details=f"Error creating contact: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
"""
@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact_route(
    request: Request,
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    try:
        user_id = getattr(current_user, "userid", None)  # safe even if user is not logged in

        enforce_permission_auto(db, current_user, "CONTACTS_SEND", request)
        result = await contact_controller.create_contact(contact, db, user_id=user_id)

        if dedupe_service.should_log_action("CONTACT_CREATE", user_id):
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_CREATE",
                user_id=user_id,
                details=f"Created new contact: {getattr(contact, 'name', 'Unnamed')}",
                request=request,
                status="active"
            )

        return result

    except HTTPException as e:
        user_id = getattr(current_user, "userid", None)
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_CREATE_FAILED",
            user_id=user_id,
            details=f"Failed to create contact: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        user_id = getattr(current_user, "userid", None)
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_CREATE_ERROR",
            user_id=user_id,
            details=f"Error creating contact: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Update Contact
# ===============================
@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    request: Request,
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        enforce_permission_auto(db, current_user, "CONTACTS", request)

        current_contact = contact_controller.get_contact_by_id(contact_id, db)
        result = contact_controller.update_contact(contact_id, contact, db)

        if dedupe_service.should_log_action("CONTACT_UPDATE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_UPDATE",
                user_id=current_user.userid,
                details=f"Updated contact ID {contact_id} (Name: {getattr(current_contact, 'name', 'N/A')})",
                request=request,
                status="active"
            )

        return result

    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_UPDATE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to update contact ID {contact_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_UPDATE_ERROR",
            user_id=current_user.userid,
            details=f"Error updating contact ID {contact_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Soft Delete Contact
# ===============================
@router.delete("/{contact_id}")
async def delete_contact(
    request: Request,
    contact_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        enforce_permission_auto(db, current_user, "CONTACTS", request)

        contact = contact_controller.get_contact_by_id(contact_id, db)
        result = contact_controller.delete_contact(contact_id, db)

        if dedupe_service.should_log_action("CONTACT_DELETE", current_user.userid):
            await system_logger.log_action(
                db=db,
                action_type="CONTACT_DELETE",
                user_id=current_user.userid,
                details=f"Soft-deleted contact ID {contact_id} (Name: {getattr(contact, 'name', 'N/A')})",
                request=request,
                status="inactive"
            )

        return result

    except HTTPException as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_DELETE_FAILED",
            user_id=current_user.userid,
            details=f"Failed to delete contact ID {contact_id}: {e.detail}",
            request=request,
            status="active"
        )
        raise e
    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_DELETE_ERROR",
            user_id=current_user.userid,
            details=f"Error deleting contact ID {contact_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ===============================
# 🔹 Hard Delete (Admin Only)
# ===============================
@router.delete("/{contact_id}/purge")
async def hard_delete_contact(
    request: Request,
    contact_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanent deletion for system admins."""
    try:
        enforce_permission_auto(db, current_user, "CONTACTS", request, admin_only=True)
        result = contact_controller.hard_delete_contact(contact_id, db)

        await system_logger.log_action(
            db=db,
            action_type="CONTACT_PURGE",
            user_id=current_user.userid,
            details=f"Permanently deleted contact ID {contact_id}",
            request=request,
            status="inactive"
        )

        return result

    except Exception as e:
        await system_logger.log_action(
            db=db,
            action_type="CONTACT_PURGE_ERROR",
            user_id=current_user.userid,
            details=f"Error permanently deleting contact ID {contact_id}: {str(e)}",
            request=request,
            status="active"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
    
# ===============================
# 🔹 Send Email (Contact Form)
# ===============================
@router.post("/contact/")
async def contact_us(
    name: str = Form(...),
    email: str = Form(None),  # Optional email for reply
    subject: str = Form("No Subject"),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        print(f"📨 Received contact form: {name}, Email: {email}, Subject: {subject}")

        # 🔹 Save contact entry first
        contact_email = email or get_config_value(db, "fromEmail", os.getenv("FROM_EMAIL"))
        contact_data = ContactCreate(
            email=contact_email,
            subject=subject,
            message=message,
            userid=None
        )

        print("💾 Saving to database...")
        db_contact = contact_controller.create_contact(contact_data, db)
        print(f"✅ Contact saved with ID: {db_contact.contactid}")

        # 🔹 Send email notification
        print("🔄 Sending notification email...")
        success = send_contact_notification(db, user_name=name, subject=subject, message=message)

        if success:
            print("✅ Email sent successfully")
            return {"message": "Thank you for your message! We'll get back to you soon."}
        else:
            print("❌ Email failed to send")
            return {"message": "Message received, but email could not be delivered."}

    except Exception as e:
        print(f"❌ Contact form error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing your message")
