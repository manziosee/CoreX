from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class InterestType(str, enum.Enum):
    SAVINGS = "SAVINGS"
    LOAN = "LOAN"
    OVERDRAFT = "OVERDRAFT"

class InterestFrequency(str, enum.Enum):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"

class InterestRate(Base):
    __tablename__ = "interest_rates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rate_code = Column(String(20), unique=True, nullable=False)
    interest_type = Column(Enum(InterestType), nullable=False)
    
    base_rate = Column(Numeric(5, 4), nullable=False)
    effective_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    
    min_balance = Column(Numeric(15, 2), default=0)
    max_balance = Column(Numeric(15, 2))
    frequency = Column(Enum(InterestFrequency), default=InterestFrequency.MONTHLY)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InterestPosting(Base):
    __tablename__ = "interest_postings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    rate_id = Column(UUID(as_uuid=True), ForeignKey("interest_rates.id"), nullable=False)
    
    posting_date = Column(DateTime(timezone=True), server_default=func.now())
    calculation_period_start = Column(DateTime(timezone=True), nullable=False)
    calculation_period_end = Column(DateTime(timezone=True), nullable=False)
    
    average_balance = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 4), nullable=False)
    interest_amount = Column(Numeric(15, 2), nullable=False)
    
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # Relationships
    account = relationship("Account")
    rate = relationship("InterestRate")
    transaction = relationship("Transaction")