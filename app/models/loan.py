from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class LoanStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DEFAULTED = "DEFAULTED"

class LoanType(str, enum.Enum):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    MORTGAGE = "MORTGAGE"
    AUTO = "AUTO"

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    loan_type = Column(Enum(LoanType), nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 4), nullable=False)  # Annual rate
    term_months = Column(String(3), nullable=False)
    monthly_payment = Column(Numeric(15, 2), nullable=False)
    
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    disbursed_amount = Column(Numeric(15, 2), default=0)
    outstanding_balance = Column(Numeric(15, 2), default=0)
    
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    approval_date = Column(DateTime(timezone=True))
    disbursement_date = Column(DateTime(timezone=True))
    maturity_date = Column(DateTime(timezone=True))
    
    purpose = Column(Text)
    collateral_description = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="loans")
    account = relationship("Account")
    payments = relationship("LoanPayment", back_populates="loan")

class LoanPayment(Base):
    __tablename__ = "loan_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    payment_number = Column(String(10), nullable=False)
    
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    amount_paid = Column(Numeric(15, 2), nullable=False)
    principal_paid = Column(Numeric(15, 2), nullable=False)
    interest_paid = Column(Numeric(15, 2), nullable=False)
    
    balance_after_payment = Column(Numeric(15, 2), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # Relationships
    loan = relationship("Loan", back_populates="payments")
    transaction = relationship("Transaction")