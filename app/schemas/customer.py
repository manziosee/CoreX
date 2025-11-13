from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from app.models.customer import KYCStatus, CustomerStatus

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: str
    customer_number: str
    kyc_status: KYCStatus
    status: CustomerStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True