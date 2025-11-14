from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.payment import BillPayment, StandingOrder, PaymentStatus
from app.core.auth import get_current_active_user, require_role
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

router = APIRouter()

class BillPaymentCreate(BaseModel):
    account_id: str
    biller_code: str
    biller_name: str
    bill_account_number: str
    amount: Decimal
    currency: str = "USD"

class BillPaymentResponse(BaseModel):
    id: str
    payment_reference: str
    biller_name: str
    amount: Decimal
    status: PaymentStatus
    payment_date: datetime
    
    class Config:
        from_attributes = True

class StandingOrderCreate(BaseModel):
    from_account_id: str
    to_account_id: Optional[str] = None
    amount: Decimal
    currency: str = "USD"
    frequency: str  # DAILY, WEEKLY, MONTHLY
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = None

class StandingOrderResponse(BaseModel):
    id: str
    order_reference: str
    amount: Decimal
    frequency: str
    next_execution_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

@router.post("/bills", response_model=BillPaymentResponse, summary="Pay Bill")
async def pay_bill(
    payment: BillPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN]))
):
    """Process a bill payment"""
    import uuid
    
    bill_payment = BillPayment(
        payment_reference=f"BILL{str(uuid.uuid4().int)[:10]}",
        account_id=payment.account_id,
        biller_code=payment.biller_code,
        biller_name=payment.biller_name,
        bill_account_number=payment.bill_account_number,
        amount=payment.amount,
        currency=payment.currency,
        status=PaymentStatus.COMPLETED
    )
    
    db.add(bill_payment)
    db.commit()
    db.refresh(bill_payment)
    return bill_payment

@router.get("/bills", response_model=List[BillPaymentResponse], summary="List Bill Payments")
async def list_bill_payments(
    account_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of bill payments"""
    query = db.query(BillPayment)
    if account_id:
        query = query.filter(BillPayment.account_id == account_id)
    
    payments = query.offset(skip).limit(limit).all()
    return payments

@router.post("/standing-orders", response_model=StandingOrderResponse, summary="Create Standing Order")
async def create_standing_order(
    order: StandingOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN]))
):
    """Create a new standing order"""
    import uuid
    
    standing_order = StandingOrder(
        order_reference=f"SO{str(uuid.uuid4().int)[:10]}",
        from_account_id=order.from_account_id,
        to_account_id=order.to_account_id,
        amount=order.amount,
        currency=order.currency,
        frequency=order.frequency,
        start_date=order.start_date,
        end_date=order.end_date,
        next_execution_date=order.start_date,
        description=order.description
    )
    
    db.add(standing_order)
    db.commit()
    db.refresh(standing_order)
    return standing_order

@router.get("/standing-orders", response_model=List[StandingOrderResponse], summary="List Standing Orders")
async def list_standing_orders(
    account_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of standing orders"""
    query = db.query(StandingOrder)
    if account_id:
        query = query.filter(StandingOrder.from_account_id == account_id)
    if is_active is not None:
        query = query.filter(StandingOrder.is_active == is_active)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.put("/standing-orders/{order_id}/cancel", summary="Cancel Standing Order")
async def cancel_standing_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN]))
):
    """Cancel a standing order"""
    order = db.query(StandingOrder).filter(StandingOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Standing order not found")
    
    order.is_active = False
    db.commit()
    return {"message": "Standing order cancelled successfully"}