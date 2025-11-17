import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.database import get_db, Base
from app.models.notification import Notification, NotificationTemplate, NotificationType, NotificationChannel, NotificationStatus
from app.models.customer import Customer, KYCStatus
from app.models.user import User, UserRole
from app.services.notification import NotificationService
from datetime import datetime
import uuid

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_notifications.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def db_session():
    """Create a test database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_customer(db_session: Session):
    """Create a test customer"""
    customer = Customer(
        id=str(uuid.uuid4()),
        customer_number="TEST001",
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        phone="+1234567890",
        kyc_status=KYCStatus.PENDING
    )
    db_session.add(customer)
    db_session.commit()
    return customer

@pytest.fixture
def test_user(db_session: Session):
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@user.com",
        hashed_password="hashed_password",
        role=UserRole.TELLER
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_create_notification(db_session: Session, test_customer: Customer):
    """Test creating a notification"""
    service = NotificationService(db_session)
    
    # Setup default templates first
    service._setup_default_templates()
    
    # Send transaction notification
    notification = service.send_transaction_notification(
        customer_id=test_customer.id,
        amount=100.0,
        transaction_type="credit"
    )
    
    assert notification.notification_type == NotificationType.TRANSACTION
    assert notification.channel == NotificationChannel.SMS
    assert "100.0" in notification.message
    assert notification.status == NotificationStatus.SENT
    assert notification.customer_id == test_customer.id

def test_get_customer_notifications(db_session: Session, test_customer: Customer):
    """Test getting customer notifications"""
    service = NotificationService(db_session)
    
    # Create test notifications
    notification1 = Notification(
        customer_id=test_customer.id,
        notification_type=NotificationType.TRANSACTION,
        channel=NotificationChannel.EMAIL,
        title="Test Notification 1",
        message="Test message 1"
    )
    notification2 = Notification(
        customer_id=test_customer.id,
        notification_type=NotificationType.KYC_UPDATE,
        channel=NotificationChannel.SMS,
        title="Test Notification 2",
        message="Test message 2"
    )
    db_session.add_all([notification1, notification2])
    db_session.commit()
    
    # Get notifications
    notifications = service.get_customer_notifications(test_customer.id)
    
    assert len(notifications) == 2
    assert notifications[0].title in ["Test Notification 1", "Test Notification 2"]
    assert notifications[1].title in ["Test Notification 1", "Test Notification 2"]

def test_mark_notification_read(db_session: Session, test_customer: Customer):
    """Test marking notification as read"""
    service = NotificationService(db_session)
    
    # Create test notification
    notification = Notification(
        customer_id=test_customer.id,
        notification_type=NotificationType.TRANSACTION,
        channel=NotificationChannel.EMAIL,
        title="Test Notification",
        message="Test message"
    )
    db_session.add(notification)
    db_session.commit()
    
    # Verify initially not read
    assert notification.read_at is None
    
    # Mark as read
    success = service.mark_as_read(str(notification.id))
    
    assert success == True
    db_session.refresh(notification)
    assert notification.read_at is not None
    assert isinstance(notification.read_at, datetime)

def test_send_kyc_notification(db_session: Session, test_customer: Customer):
    """Test sending KYC status notification"""
    service = NotificationService(db_session)
    service._setup_default_templates()
    
    # Send KYC notification
    notification = service.send_kyc_notification(test_customer.id, "APPROVED")
    
    assert notification.notification_type == NotificationType.KYC_UPDATE
    assert notification.channel == NotificationChannel.EMAIL
    assert "APPROVED" in notification.message
    assert notification.status == NotificationStatus.SENT
    assert notification.customer_id == test_customer.id

def test_notification_template_creation(db_session: Session):
    """Test creating notification templates"""
    service = NotificationService(db_session)
    
    # Create custom template
    template = service.create_template(
        template_code="CUSTOM_ALERT",
        notification_type=NotificationType.SYSTEM_ALERT,
        title_template="Custom Alert: {type}",
        message_template="Alert message: {content} at {time}"
    )
    
    assert template.template_code == "CUSTOM_ALERT"
    assert template.notification_type == NotificationType.SYSTEM_ALERT
    assert template.is_active == True
    assert "{type}" in template.title_template
    assert "{content}" in template.message_template

def test_setup_default_templates(db_session: Session):
    """Test setting up default notification templates"""
    service = NotificationService(db_session)
    
    # Setup default templates
    service._setup_default_templates()
    
    # Check if templates were created
    transaction_template = db_session.query(NotificationTemplate).filter(
        NotificationTemplate.template_code == "TRANSACTION_ALERT"
    ).first()
    
    kyc_template = db_session.query(NotificationTemplate).filter(
        NotificationTemplate.template_code == "KYC_UPDATE"
    ).first()
    
    assert transaction_template is not None
    assert transaction_template.notification_type == NotificationType.TRANSACTION
    assert kyc_template is not None
    assert kyc_template.notification_type == NotificationType.KYC_UPDATE

def test_notification_filtering_and_pagination(db_session: Session, test_customer: Customer):
    """Test notification filtering and pagination"""
    service = NotificationService(db_session)
    
    # Create multiple notifications
    notifications = []
    for i in range(15):
        notification = Notification(
            customer_id=test_customer.id,
            notification_type=NotificationType.TRANSACTION,
            channel=NotificationChannel.EMAIL,
            title=f"Notification {i}",
            message=f"Message {i}"
        )
        notifications.append(notification)
    
    db_session.add_all(notifications)
    db_session.commit()
    
    # Test pagination
    first_batch = service.get_customer_notifications(test_customer.id, limit=10)
    second_batch = service.get_customer_notifications(test_customer.id, limit=5)
    
    assert len(first_batch) == 10
    assert len(second_batch) == 5
    
    # Verify they're ordered by creation time (newest first)
    assert first_batch[0].created_at >= first_batch[1].created_at

def test_notification_service_error_handling(db_session: Session):
    """Test notification service error handling"""
    service = NotificationService(db_session)
    
    # Test marking non-existent notification as read
    success = service.mark_as_read("non-existent-id")
    assert success == False
    
    # Test getting notifications for non-existent customer
    notifications = service.get_customer_notifications("non-existent-customer")
    assert len(notifications) == 0

def test_notification_template_fallback(db_session: Session, test_customer: Customer):
    """Test notification template fallback mechanism"""
    service = NotificationService(db_session)
    
    # Don't setup default templates to test fallback
    notification = service.send_transaction_notification(
        customer_id=test_customer.id,
        amount=50.0,
        transaction_type="debit"
    )
    
    # Should use fallback template
    assert notification.title == "CoreX Notification"
    assert "CoreX Banking" in notification.message