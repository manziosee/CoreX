from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationTemplate, NotificationType, NotificationChannel, NotificationStatus
from app.schemas.notification import NotificationCreate
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        notification = Notification(**notification_data.dict())
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def send_transaction_notification(self, customer_id: str, amount: float, transaction_type: str) -> Notification:
        """Send transaction notification"""
        template = self._get_template("TRANSACTION_ALERT")
        
        title = template.title_template.format(type=transaction_type)
        message = template.message_template.format(
            amount=amount,
            type=transaction_type,
            time=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        notification = Notification(
            customer_id=customer_id,
            notification_type=NotificationType.TRANSACTION,
            channel=NotificationChannel.SMS,
            title=title,
            message=message,
            status=NotificationStatus.SENT,
            sent_at=datetime.utcnow()
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    def send_kyc_notification(self, customer_id: str, status: str) -> Notification:
        """Send KYC status update notification"""
        template = self._get_template("KYC_UPDATE")
        
        title = template.title_template
        message = template.message_template.format(status=status)
        
        notification = Notification(
            customer_id=customer_id,
            notification_type=NotificationType.KYC_UPDATE,
            channel=NotificationChannel.EMAIL,
            title=title,
            message=message,
            status=NotificationStatus.SENT,
            sent_at=datetime.utcnow()
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    def get_customer_notifications(self, customer_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications for a customer"""
        return self.db.query(Notification).filter(
            Notification.customer_id == customer_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def create_template(self, template_code: str, notification_type: NotificationType, 
                       title_template: str, message_template: str) -> NotificationTemplate:
        """Create notification template"""
        template = NotificationTemplate(
            template_code=template_code,
            notification_type=notification_type,
            title_template=title_template,
            message_template=message_template
        )
        self.db.add(template)
        self.db.commit()
        return template
    
    def _get_template(self, template_code: str) -> NotificationTemplate:
        """Get notification template by code"""
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.template_code == template_code,
            NotificationTemplate.is_active == True
        ).first()
        
        if not template:
            # Return default template
            return NotificationTemplate(
                title_template="CoreX Notification",
                message_template="You have a new notification from CoreX Banking."
            )
        
        return template
    
    def _setup_default_templates(self):
        """Setup default notification templates"""
        templates = [
            {
                "template_code": "TRANSACTION_ALERT",
                "notification_type": NotificationType.TRANSACTION,
                "title_template": "{type} Transaction Alert",
                "message_template": "Your account has been {type} with {amount}. Time: {time}"
            },
            {
                "template_code": "KYC_UPDATE",
                "notification_type": NotificationType.KYC_UPDATE,
                "title_template": "KYC Status Update",
                "message_template": "Your KYC verification status has been updated to: {status}"
            }
        ]
        
        for template_data in templates:
            existing = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.template_code == template_data["template_code"]
            ).first()
            
            if not existing:
                template = NotificationTemplate(**template_data)
                self.db.add(template)
        
        self.db.commit()