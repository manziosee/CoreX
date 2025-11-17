from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType, NotificationChannel, NotificationStatus

class NotificationCreate(BaseModel):
    customer_id: Optional[str] = None
    user_id: Optional[str] = None
    notification_type: NotificationType
    channel: NotificationChannel
    title: str
    message: str

class NotificationResponse(BaseModel):
    id: str
    notification_type: NotificationType
    channel: NotificationChannel
    title: str
    message: str
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationTemplateCreate(BaseModel):
    template_code: str
    notification_type: NotificationType
    title_template: str
    message_template: str

class NotificationTemplateResponse(BaseModel):
    id: str
    template_code: str
    notification_type: NotificationType
    title_template: str
    message_template: str
    is_active: bool
    
    class Config:
        from_attributes = True