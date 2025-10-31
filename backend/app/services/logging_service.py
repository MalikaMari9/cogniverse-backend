from fastapi import Request
from sqlalchemy.orm import Session
from app.db.schemas.system_log_schema import SystemLogCreate
from app.controllers.system_log_controller import create_log

class SystemLogger:
    @staticmethod
    async def log_action(
        db: Session,
        action_type: str,
        user_id: int = None,
        details: str = None,
        request: Request = None,
        status: str = "active"
    ):
        """Log system actions with user context"""
        try:
            ip_address = None
            browser_info = None
            
            if request:
                ip_address = request.client.host
                browser_info = request.headers.get("user-agent", "")[:200]
            
            log_data = SystemLogCreate(
                action_type=action_type,
                userid=user_id,
                details=details,
                ip_address=ip_address,
                browser_info=browser_info,
                status=status
            )
            
            # ✅ FIXED ARGUMENT ORDER
            return create_log(db, log_data)

        except Exception as e:
            print(f"Logging failed: {e}")
            # Don't break the main functionality if logging fails


# Global instance
system_logger = SystemLogger()
