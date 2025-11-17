from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class NotificationType(str, enum.Enum):
    TRANSACTION = "TRANSACTION"
    KYC_UPDATE = "KYC_UPDATE"
    LOAN_UPDATE = "LOAN_UPDATE"
    ACCOUNT_UPDATE = "ACCOUNT_UPDATE"
    SYSTEM_ALERT = "SYSTEM_ALERT"

class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    IN_APP = "IN_APP"

class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer")
    user = relationship("User")

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_code = Column(String(50), unique=True, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())