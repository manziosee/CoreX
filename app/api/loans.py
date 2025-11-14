from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import LoanApplicationCreate, LoanResponse, LoanApproval, LoanPaymentCreate, LoanPaymentResponse
from app.services.loan import LoanService
from app.core.auth import get_current_active_user, require_role
from typing import List

router = APIRouter()

@router.post("/applications", response_model=LoanResponse, summary="Apply for Loan")
async def apply_for_loan(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN]))
):
    """Submit a new loan application"""
    service = LoanService(db)
    loan = service.apply_for_loan(application)
    return loan

@router.get("/applications", response_model=List[LoanResponse], summary="List Loan Applications")
async def list_loan_applications(
    status: LoanStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN, UserRole.AUDITOR]))
):
    """Get list of loan applications"""
    query = db.query(Loan)
    if status:
        query = query.filter(Loan.status == status)
    
    loans = query.offset(skip).limit(limit).all()
    return loans

@router.get("/{loan_id}", response_model=LoanResponse, summary="Get Loan Details")
async def get_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get loan details by ID"""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

@router.put("/{loan_id}/approve", response_model=LoanResponse, summary="Approve Loan")
async def approve_loan(
    loan_id: str,
    approval: LoanApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Approve a loan application"""
    service = LoanService(db)
    try:
        loan = service.approve_loan(loan_id, approval)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{loan_id}/disburse", summary="Disburse Loan")
async def disburse_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Disburse approved loan to customer account"""
    service = LoanService(db)
    success = service.disburse_loan(loan_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disburse loan")
    return {"message": "Loan disbursed successfully"}

@router.post("/{loan_id}/payments", response_model=LoanPaymentResponse, summary="Make Loan Payment")
async def make_loan_payment(
    loan_id: str,
    payment_data: LoanPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TELLER, UserRole.ADMIN]))
):
    """Process a loan payment"""
    payment_data.loan_id = loan_id
    service = LoanService(db)
    try:
        payment = service.make_payment(payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{loan_id}/payments", response_model=List[LoanPaymentResponse], summary="Get Loan Payments")
async def get_loan_payments(
    loan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payment history for a loan"""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan.payments

@router.get("/customer/{customer_id}", response_model=List[LoanResponse], summary="Get Customer Loans")
async def get_customer_loans(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all loans for a specific customer"""
    loans = db.query(Loan).filter(Loan.customer_id == customer_id).all()
    return loans