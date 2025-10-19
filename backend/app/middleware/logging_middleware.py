from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.services.logging_service import system_logger
from app.db.database import get_db
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip logging for CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip logging for certain paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        start_time = time.time()
        
        # Get database session
        db = next(get_db())
        
        try:
            response = await call_next(request)
            
            # Log based on status code and method
            if response.status_code >= 400:
                await system_logger.log_action(
                    db=db,
                    action_type=f"http_{request.method.lower()}_error",
                    user_id=None,
                    details=f"{request.method} {request.url.path} - Status: {response.status_code}",
                    request=request,
                    status="active"
                )
            
            process_time = time.time() - start_time
            
            # Log slow requests
            if process_time > 5.0:  # 5 seconds threshold
                await system_logger.log_action(
                    db=db,
                    action_type="slow_request",
                    user_id=None,
                    details=f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s",
                    request=request,
                    status="active"
                )
                
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            await system_logger.log_action(
                db=db,
                action_type="server_error",
                user_id=None,
                details=f"Server error in {request.method} {request.url.path}: {str(e)}",
                request=request,
                status="active"
            )
            raise
        finally:
            # Important: Close the database session
            db.close()