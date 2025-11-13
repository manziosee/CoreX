from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base

class DocumentType(str, enum.Enum):
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    UTILITY_BILL = "UTILITY_BILL"
    BANK_STATEMENT = "BANK_STATEMENT"

class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(100))
    file_path = Column(String(500))
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rejection_reason = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="kyc_documents")
    verifier = relationship("User")