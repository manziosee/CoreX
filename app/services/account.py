from sqlalchemy.orm import Session
from app.models.account import Account, Balance
from app.schemas.account import AccountCreate
from typing import List, Optional
import uuid

class AccountService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_account(self, account_data: AccountCreate) -> Account:
        # Generate account number
        account_number = f"AC{str(uuid.uuid4().int)[:10]}"
        
        account = Account(
            account_number=account_number,
            **account_data.dict()
        )
        self.db.add(account)
        self.db.flush()  # Get the account ID
        
        # Create initial balance record
        balance = Balance(
            account_id=account.id,
            ledger_balance=0.00,
            available_balance=0.00
        )
        self.db.add(balance)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.account_number == account_number).first()
    
    def get_balance(self, account_id: str) -> Optional[Balance]:
        return self.db.query(Balance).filter(Balance.account_id == account_id).first()
    
    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        return self.db.query(Account).filter(Account.customer_id == customer_id).all()
    
    def update_balance(self, account_id: str, ledger_balance: float, available_balance: float) -> Optional[Balance]:
        balance = self.get_balance(account_id)
        if balance:
            balance.ledger_balance = ledger_balance
            balance.available_balance = available_balance
            self.db.commit()
            self.db.refresh(balance)
        return balance