from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class PaymentType(str, enum.Enum):
    BILL_PAYMENT = "BILL_PAYMENT"
    MOBILE_MONEY = "MOBILE_MONEY"
    CARD_PAYMENT = "CARD_PAYMENT"
    STANDING_ORDER = "STANDING_ORDER"
    BULK_TRANSFER = "BULK_TRANSFER"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class BillPayment(Base):
    __tablename__ = "bill_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_reference = Column(String(50), unique=True, nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    biller_code = Column(String(20), nullable=False)
    biller_name = Column(String(100), nullable=False)
    bill_account_number = Column(String(50), nullable=False)
    
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # Relationships
    account = relationship("Account")
    transaction = relationship("Transaction")

class StandingOrder(Base):
    __tablename__ = "standing_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_reference = Column(String(50), unique=True, nullable=False)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD")
    frequency = Column(String(20), nullable=False)  # DAILY, WEEKLY, MONTHLY
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    next_execution_date = Column(DateTime(timezone=True), nullable=False)
    
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
    executions = relationship("StandingOrderExecution", back_populates="standing_order")

class StandingOrderExecution(Base):
    __tablename__ = "standing_order_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standing_order_id = Column(UUID(as_uuid=True), ForeignKey("standing_orders.id"), nullable=False)
    
    execution_date = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    failure_reason = Column(Text)
    
    # Relationships
    standing_order = relationship("StandingOrder", back_populates="executions")
    transaction = relationship("Transaction")