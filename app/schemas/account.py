from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.account import AccountType, AccountStatus

class AccountBase(BaseModel):
    account_type: AccountType
    currency: str = "USD"

class AccountCreate(AccountBase):
    customer_id: str

class AccountResponse(AccountBase):
    id: str
    account_number: str
    customer_id: str
    status: AccountStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    account_id: str
    ledger_balance: Decimal
    available_balance: Decimal
    updated_at: datetime
    
    class Config:
        from_attributes = True