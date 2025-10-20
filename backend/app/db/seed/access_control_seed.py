from sqlalchemy.orm import Session
from app.db.models.access_control_model import AccessControl, AccessLevel, LifecycleStatus
import enum

def seed_access_controls(db: Session):
    """Insert default access control modules if they don't already exist."""

    defaults = [
        # --- Core system modules ---
        {
            "module_key": "PROJECTS",
            "module_desc": "Manage AI simulation projects",
            "user_access": AccessLevel.write,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "AGENTS",
            "module_desc": "Manage AI agents and profiles",
            "user_access": AccessLevel.write,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "RELATIONSHIPS",
            "module_desc": "Manage agent relationships",
            "user_access": AccessLevel.write,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "SCENARIOS",
            "module_desc": "Create and manage simulation scenarios",
            "user_access": AccessLevel.write,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "RESULTS",
            "module_desc": "View simulation results",
            "user_access": AccessLevel.read,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "BILLING",
            "module_desc": "Billing and credit transactions",
            "user_access": AccessLevel.write,   # ✅ users can manage payments
            "admin_access": AccessLevel.read,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "USER_MANAGEMENT",
            "module_desc": "Manage user accounts",
            "user_access": AccessLevel.none,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "ACCESS_CONTROL",
            "module_desc": "Manage access modules and permissions",
            "user_access": AccessLevel.none,
            "admin_access": AccessLevel.read,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "CONFIGURATION",
            "module_desc": "System configuration and global settings",
            "user_access": AccessLevel.none,
            "admin_access": AccessLevel.read,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "ANNOUNCEMENTS",
            "module_desc": "System-wide announcements",
            "user_access": AccessLevel.read,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "NOTIFICATIONS",
            "module_desc": "System notifications",
            "user_access": AccessLevel.read,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "SYSTEM_LOGS",
            "module_desc": "View system activity logs",
            "user_access": AccessLevel.none,
            "admin_access": AccessLevel.read,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "MAINTENANCE",
            "module_desc": "Enable or disable maintenance mode",
            "user_access": AccessLevel.none,
            "admin_access": AccessLevel.read,
            "superadmin_access": AccessLevel.write,
            "is_critical": True,
            "status": LifecycleStatus.active,
        },
        {
            "module_key": "PROFILE",
            "module_desc": "User profile and password management",
            "user_access": AccessLevel.write,
            "admin_access": AccessLevel.write,
            "superadmin_access": AccessLevel.write,
            "is_critical": False,
            "status": LifecycleStatus.active,
        },
    ]

    added = 0
    for entry in defaults:
        existing = db.query(AccessControl).filter(AccessControl.module_key == entry["module_key"]).first()
        if not existing:
            db.add(AccessControl(**entry))
            added += 1


    db.commit()
    print(f"✅ Access control seeding complete. {added} new module(s) added.")
