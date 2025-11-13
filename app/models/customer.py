from sqlalchemy import Column, String, Date, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base

class KYCStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CustomerStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_number = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    occupation = Column(String(100))
    income_range = Column(String(50))
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    accounts = relationship("Account", back_populates="customer")
    kyc_documents = relationship("KYCDocument", back_populates="customer")