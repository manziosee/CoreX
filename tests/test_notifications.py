import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models.notification import Notification, NotificationTemplate, NotificationType, NotificationChannel
from app.services.notification import NotificationService

client = TestClient(app)

def test_create_notification(db_session: Session):
    """Test creating a notification"""
    service = NotificationService(db_session)
    
    # Setup default templates first
    service._setup_default_templates()
    
    # Send transaction notification
    notification = service.send_transaction_notification(
        customer_id="test-customer-id",
        amount=100.0,
        transaction_type="credit"
    )
    
    assert notification.notification_type == NotificationType.TRANSACTION
    assert notification.channel == NotificationChannel.SMS
    assert "100.0" in notification.message

def test_create_notification_template(db_session: Session):
    """Test creating notification template"""
    service = NotificationService(db_session)
    
    template = service.create_template(
        template_code="TEST_TEMPLATE",
        notification_type=NotificationType.SYSTEM_ALERT,
        title_template="Test Alert",
        message_template="This is a test message: {content}"
    )
    
    assert template.template_code == "TEST_TEMPLATE"
    assert template.is_active == True

def test_get_customer_notifications(db_session: Session):
    """Test getting customer notifications"""
    service = NotificationService(db_session)
    
    # Create test notification
    notification = Notification(
        customer_id="test-customer-id",
        notification_type=NotificationType.TRANSACTION,
        channel=NotificationChannel.EMAIL,
        title="Test Notification",
        message="Test message"
    )
    db_session.add(notification)
    db_session.commit()
    
    # Get notifications
    notifications = service.get_customer_notifications("test-customer-id")
    
    assert len(notifications) == 1
    assert notifications[0].title == "Test Notification"

def test_mark_notification_read(db_session: Session):
    """Test marking notification as read"""
    service = NotificationService(db_session)
    
    # Create test notification
    notification = Notification(
        customer_id="test-customer-id",
        notification_type=NotificationType.TRANSACTION,
        channel=NotificationChannel.EMAIL,
        title="Test Notification",
        message="Test message"
    )
    db_session.add(notification)
    db_session.commit()
    
    # Mark as read
    success = service.mark_as_read(str(notification.id))
    
    assert success == True
    db_session.refresh(notification)
    assert notification.read_at is not None