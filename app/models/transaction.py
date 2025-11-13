from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, DECIMAL, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base

class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    FEE = "FEE"
    INTEREST = "INTEREST"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class EntryType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(50), unique=True, nullable=False)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    entries = relationship("Entry", back_populates="transaction")

class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    entry_type = Column(Enum(EntryType), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    transaction = relationship("Transaction", back_populates="entries")
    account = relationship("Account")