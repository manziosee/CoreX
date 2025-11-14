from sqlalchemy.orm import Session
from app.models.interest import InterestRate, InterestPosting, InterestType, InterestFrequency
from app.models.account import Account, Balance, AccountType
from app.models.transaction import Transaction, TransactionType
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

class InterestService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_interest_rate(self, rate_code: str, interest_type: InterestType, 
                           base_rate: Decimal, min_balance: Decimal = 0) -> InterestRate:
        """Create new interest rate"""
        rate = InterestRate(
            rate_code=rate_code,
            interest_type=interest_type,
            base_rate=base_rate,
            min_balance=min_balance,
            effective_date=datetime.utcnow()
        )
        self.db.add(rate)
        self.db.commit()
        self.db.refresh(rate)
        return rate
    
    def calculate_savings_interest(self, account_id: str, period_days: int = 30) -> Decimal:
        """Calculate interest for savings account"""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account or account.account_type != AccountType.SAVINGS:
            return Decimal('0')
        
        balance = self.db.query(Balance).filter(Balance.account_id == account_id).first()
        if not balance or balance.ledger_balance <= 0:
            return Decimal('0')
        
        # Get applicable interest rate
        rate = self.db.query(InterestRate).filter(
            InterestRate.interest_type == InterestType.SAVINGS,
            InterestRate.is_active == True,
            InterestRate.min_balance <= balance.ledger_balance
        ).order_by(InterestRate.min_balance.desc()).first()
        
        if not rate:
            return Decimal('0')
        
        # Calculate interest (simple daily calculation)
        daily_rate = rate.base_rate / 365
        interest_amount = Decimal(str(balance.ledger_balance)) * daily_rate * period_days
        
        return interest_amount.quantize(Decimal('0.01'))
    
    def post_monthly_interest(self) -> int:
        """Post monthly interest for all eligible savings accounts"""
        posted_count = 0
        
        # Get all active savings accounts
        savings_accounts = self.db.query(Account).filter(
            Account.account_type == AccountType.SAVINGS,
            Account.status == "ACTIVE"
        ).all()
        
        for account in savings_accounts:
            try:
                interest_amount = self.calculate_savings_interest(account.id, 30)
                
                if interest_amount > 0:
                    # Create interest posting record
                    posting = InterestPosting(
                        account_id=account.id,
                        rate_id=self._get_savings_rate_id(),
                        calculation_period_start=datetime.utcnow() - timedelta(days=30),
                        calculation_period_end=datetime.utcnow(),
                        average_balance=self._get_account_balance(account.id),
                        interest_rate=self._get_savings_rate(),
                        interest_amount=interest_amount
                    )
                    
                    # Create credit transaction
                    transaction = Transaction(
                        transaction_id=f"INT{str(uuid.uuid4().int)[:10]}",
                        to_account_id=account.id,
                        amount=interest_amount,
                        currency=account.currency,
                        transaction_type=TransactionType.CREDIT,
                        description="Monthly interest credit"
                    )
                    
                    # Update account balance
                    balance = self.db.query(Balance).filter(Balance.account_id == account.id).first()
                    if balance:
                        balance.ledger_balance += float(interest_amount)
                        balance.available_balance += float(interest_amount)
                    
                    posting.transaction_id = transaction.id
                    
                    self.db.add(posting)
                    self.db.add(transaction)
                    posted_count += 1
                    
            except Exception as e:
                print(f"Error posting interest for account {account.id}: {e}")
                continue
        
        self.db.commit()
        return posted_count
    
    def _get_savings_rate_id(self) -> str:
        """Get active savings interest rate ID"""
        rate = self.db.query(InterestRate).filter(
            InterestRate.interest_type == InterestType.SAVINGS,
            InterestRate.is_active == True
        ).first()
        return str(rate.id) if rate else None
    
    def _get_savings_rate(self) -> Decimal:
        """Get active savings interest rate"""
        rate = self.db.query(InterestRate).filter(
            InterestRate.interest_type == InterestType.SAVINGS,
            InterestRate.is_active == True
        ).first()
        return rate.base_rate if rate else Decimal('0')
    
    def _get_account_balance(self, account_id: str) -> Decimal:
        """Get account balance"""
        balance = self.db.query(Balance).filter(Balance.account_id == account_id).first()
        return Decimal(str(balance.ledger_balance)) if balance else Decimal('0')