from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationTemplateCreate, NotificationTemplateResponse
from app.services.notification import NotificationService
from app.core.auth import get_current_active_user, require_role
from typing import List

router = APIRouter()

@router.post("/", response_model=NotificationResponse, summary="Create Notification")
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TELLER]))
):
    """Create a new notification"""
    service = NotificationService(db)
    return service.create_notification(notification)

@router.get("/customer/{customer_id}", response_model=List[NotificationResponse], summary="Get Customer Notifications")
async def get_customer_notifications(
    customer_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notifications for a customer"""
    service = NotificationService(db)
    return service.get_customer_notifications(customer_id, limit)

@router.put("/{notification_id}/read", summary="Mark as Read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark notification as read"""
    service = NotificationService(db)
    success = service.mark_as_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.post("/templates", response_model=NotificationTemplateResponse, summary="Create Template")
async def create_notification_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create notification template"""
    service = NotificationService(db)
    return service.create_template(
        template.template_code,
        template.notification_type,
        template.title_template,
        template.message_template
    )

@router.post("/setup-defaults", summary="Setup Default Templates")
async def setup_default_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Setup default notification templates"""
    service = NotificationService(db)
    service._setup_default_templates()
    return {"message": "Default templates created successfully"}