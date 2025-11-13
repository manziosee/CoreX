from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    transaction_id: str
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    status: TransactionStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True