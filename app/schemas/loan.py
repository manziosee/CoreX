from pydantic import BaseModel, validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from app.models.loan import LoanStatus, LoanType

class LoanApplicationCreate(BaseModel):
    customer_id: str
    loan_type: LoanType
    principal_amount: Decimal
    term_months: int
    purpose: str
    collateral_description: Optional[str] = None
    
    @validator('principal_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Principal amount must be positive')
        return v
    
    @validator('term_months')
    def validate_term(cls, v):
        if v < 1 or v > 360:
            raise ValueError('Term must be between 1 and 360 months')
        return v

class LoanResponse(BaseModel):
    id: str
    loan_number: str
    customer_id: str
    loan_type: LoanType
    principal_amount: Decimal
    interest_rate: Decimal
    term_months: str
    monthly_payment: Decimal
    status: LoanStatus
    outstanding_balance: Decimal
    application_date: datetime
    approval_date: Optional[datetime]
    
    class Config:
        from_attributes = True

class LoanApproval(BaseModel):
    interest_rate: Decimal
    approved_amount: Optional[Decimal] = None
    
    @validator('interest_rate')
    def validate_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Interest rate must be between 0 and 100')
        return v

class LoanPaymentCreate(BaseModel):
    loan_id: str
    amount_paid: Decimal
    
    @validator('amount_paid')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be positive')
        return v

class LoanPaymentResponse(BaseModel):
    id: str
    payment_number: str
    payment_date: datetime
    amount_paid: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    balance_after_payment: Decimal
    
    class Config:
        from_attributes = True