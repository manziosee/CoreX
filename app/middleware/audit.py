from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.audit import AuditLog, ActionType
import json
import uuid
from datetime import datetime

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests for audit purposes"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit for health checks and docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        start_time = datetime.utcnow()
        
        # Get request body for POST/PUT requests
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = body.decode('utf-8')
            except:
                request_body = None
        
        # Process the request
        response = await call_next(request)
        
        # Log the audit entry
        try:
            await self._log_audit_entry(
                request=request,
                response=response,
                request_body=request_body,
                start_time=start_time
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            print(f"Audit logging failed: {e}")
        
        return response
    
    async def _log_audit_entry(self, request: Request, response: Response, request_body: str, start_time: datetime):
        """Log audit entry to database"""
        db = SessionLocal()
        
        try:
            # Determine action type based on HTTP method and path
            action_type = self._get_action_type(request.method, request.url.path)
            
            # Create audit log entry
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=None,  # Will be populated by auth system
                action_type=action_type,
                resource_type=self._get_resource_type(request.url.path),
                resource_id=self._extract_resource_id(request.url.path),
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "status_code": response.status_code,
                    "user_agent": request.headers.get("User-Agent"),
                    "ip_address": request.client.host if request.client else None
                },
                timestamp=start_time
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            db.rollback()
        finally:
            db.close()
    
    def _get_action_type(self, method: str, path: str) -> ActionType:
        """Determine action type based on HTTP method"""
        if method == "GET":
            return ActionType.READ
        elif method == "POST":
            if "login" in path or "token" in path:
                return ActionType.LOGIN
            return ActionType.CREATE
        elif method in ["PUT", "PATCH"]:
            return ActionType.UPDATE
        elif method == "DELETE":
            return ActionType.DELETE
        else:
            return ActionType.OTHER
    
    def _get_resource_type(self, path: str) -> str:
        """Extract resource type from path"""
        path_parts = path.strip("/").split("/")
        if len(path_parts) > 0:
            return path_parts[0].upper()
        return "UNKNOWN"
    
    def _extract_resource_id(self, path: str) -> str:
        """Extract resource ID from path if present"""
        path_parts = path.strip("/").split("/")
        for part in path_parts:
            if part.isdigit() or (len(part) > 10 and "-" in part):
                return part
        return None