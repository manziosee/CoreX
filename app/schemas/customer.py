from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from app.models.customer import KYCStatus, CustomerStatus
from .kyc import KYCDocumentResponse

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerOnboarding(CustomerBase):
    """Enhanced customer creation with address and additional info"""
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    occupation: Optional[str] = None
    income_range: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: str
    customer_number: str
    kyc_status: KYCStatus
    status: CustomerStatus
    created_at: datetime
    updated_at: datetime
    kyc_documents: Optional[List[KYCDocumentResponse]] = []
    
    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    """Detailed customer response with additional fields"""
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    occupation: Optional[str] = None
    income_range: Optional[str] = None

class KYCStatusUpdate(BaseModel):
    kyc_status: KYCStatus
    reason: Optional[str] = None