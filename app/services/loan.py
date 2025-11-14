from sqlalchemy.orm import Session
from app.models.loan import Loan, LoanPayment, LoanStatus, LoanType
from app.models.account import Account, Balance
from app.models.transaction import Transaction, TransactionType
from app.schemas.loan import LoanApplicationCreate, LoanApproval, LoanPaymentCreate
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
import math

class LoanService:
    def __init__(self, db: Session):
        self.db = db
    
    def apply_for_loan(self, application: LoanApplicationCreate) -> Loan:
        """Create a new loan application"""
        loan_number = f"LN{str(uuid.uuid4().int)[:10]}"
        
        # Calculate monthly payment (simple calculation)
        monthly_rate = Decimal('0.12') / 12  # Default 12% annual rate
        monthly_payment = self._calculate_monthly_payment(
            application.principal_amount, 
            monthly_rate, 
            application.term_months
        )
        
        loan = Loan(
            loan_number=loan_number,
            customer_id=application.customer_id,
            account_id=self._get_customer_account(application.customer_id),
            loan_type=application.loan_type,
            principal_amount=application.principal_amount,
            interest_rate=Decimal('12.0000'),  # Default rate
            term_months=str(application.term_months),
            monthly_payment=monthly_payment,
            outstanding_balance=application.principal_amount,
            purpose=application.purpose,
            collateral_description=application.collateral_description
        )
        
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan
    
    def approve_loan(self, loan_id: str, approval: LoanApproval) -> Loan:
        """Approve a loan application"""
        loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan or loan.status != LoanStatus.PENDING:
            raise ValueError("Loan not found or not in pending status")
        
        # Update loan with approval details
        approved_amount = approval.approved_amount or loan.principal_amount
        loan.principal_amount = approved_amount
        loan.interest_rate = approval.interest_rate
        loan.outstanding_balance = approved_amount
        
        # Recalculate monthly payment
        monthly_rate = approval.interest_rate / 100 / 12
        loan.monthly_payment = self._calculate_monthly_payment(
            approved_amount, monthly_rate, int(loan.term_months)
        )
        
        loan.status = LoanStatus.APPROVED
        loan.approval_date = datetime.utcnow()
        loan.maturity_date = datetime.utcnow() + timedelta(days=int(loan.term_months) * 30)
        
        self.db.commit()
        return loan
    
    def disburse_loan(self, loan_id: str) -> bool:
        """Disburse approved loan to customer account"""
        loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan or loan.status != LoanStatus.APPROVED:
            return False
        
        try:
            # Create disbursement transaction
            transaction = Transaction(
                transaction_id=f"DISB{str(uuid.uuid4().int)[:10]}",
                to_account_id=loan.account_id,
                amount=loan.principal_amount,
                currency="USD",
                transaction_type=TransactionType.CREDIT,
                description=f"Loan disbursement - {loan.loan_number}"
            )
            self.db.add(transaction)
            
            # Update account balance
            balance = self.db.query(Balance).filter(Balance.account_id == loan.account_id).first()
            if balance:
                balance.ledger_balance += float(loan.principal_amount)
                balance.available_balance += float(loan.principal_amount)
            
            # Update loan status
            loan.status = LoanStatus.ACTIVE
            loan.disbursed_amount = loan.principal_amount
            loan.disbursement_date = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def make_payment(self, payment_data: LoanPaymentCreate) -> LoanPayment:
        """Process loan payment"""
        loan = self.db.query(Loan).filter(Loan.id == payment_data.loan_id).first()
        if not loan or loan.status != LoanStatus.ACTIVE:
            raise ValueError("Loan not found or not active")
        
        # Calculate interest and principal portions
        monthly_rate = loan.interest_rate / 100 / 12
        interest_portion = loan.outstanding_balance * monthly_rate
        principal_portion = payment_data.amount_paid - interest_portion
        
        if principal_portion < 0:
            principal_portion = Decimal('0')
            interest_portion = payment_data.amount_paid
        
        # Create payment record
        payment_number = f"PMT{len(loan.payments) + 1:03d}"
        payment = LoanPayment(
            loan_id=loan.id,
            payment_number=payment_number,
            amount_paid=payment_data.amount_paid,
            principal_paid=principal_portion,
            interest_paid=interest_portion,
            balance_after_payment=loan.outstanding_balance - principal_portion
        )
        
        # Update loan balance
        loan.outstanding_balance -= principal_portion
        if loan.outstanding_balance <= 0:
            loan.status = LoanStatus.CLOSED
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def _calculate_monthly_payment(self, principal: Decimal, monthly_rate: Decimal, months: int) -> Decimal:
        """Calculate monthly payment using loan formula"""
        if monthly_rate == 0:
            return principal / months
        
        rate_float = float(monthly_rate)
        principal_float = float(principal)
        
        payment = principal_float * (rate_float * (1 + rate_float) ** months) / ((1 + rate_float) ** months - 1)
        return Decimal(str(round(payment, 2)))
    
    def _get_customer_account(self, customer_id: str) -> str:
        """Get customer's primary account"""
        account = self.db.query(Account).filter(Account.customer_id == customer_id).first()
        return str(account.id) if account else None