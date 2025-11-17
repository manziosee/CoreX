from sqlalchemy.orm import Session
from app.models.transaction import Transaction, Entry, TransactionStatus, EntryType
from app.models.account import Balance, Account
from app.schemas.transaction import TransactionCreate
from typing import List, Optional
from datetime import datetime
import uuid

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        # Generate transaction ID
        transaction_id = f"TXN{str(uuid.uuid4().int)[:12]}"
        
        transaction = Transaction(
            transaction_id=transaction_id,
            **transaction_data.dict()
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_account_transactions(self, account_id: str, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).filter(
            (Transaction.from_account_id == account_id) | 
            (Transaction.to_account_id == account_id)
        ).offset(skip).limit(limit).all()
    
    def process_transaction(self, transaction_id: str) -> bool:
        transaction = self.get_transaction(transaction_id)
        if not transaction or transaction.status != TransactionStatus.PENDING:
            return False
        
        try:
            # Create double-entry records
            if transaction.from_account_id:
                # Debit from source account
                debit_entry = Entry(
                    transaction_id=transaction.id,
                    account_id=transaction.from_account_id,
                    entry_type=EntryType.DEBIT,
                    amount=transaction.amount
                )
                self.db.add(debit_entry)
                
                # Update source account balance
                self._update_account_balance(transaction.from_account_id, -float(transaction.amount))
            
            if transaction.to_account_id:
                # Credit to destination account
                credit_entry = Entry(
                    transaction_id=transaction.id,
                    account_id=transaction.to_account_id,
                    entry_type=EntryType.CREDIT,
                    amount=transaction.amount
                )
                self.db.add(credit_entry)
                
                # Update destination account balance
                self._update_account_balance(transaction.to_account_id, float(transaction.amount))
            
            # Update transaction status
            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.utcnow()
            
            # Send notifications
            self._send_transaction_notifications(transaction)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            transaction.status = TransactionStatus.FAILED
            self.db.commit()
            return False
    
    def _update_account_balance(self, account_id: str, amount: float):
        balance = self.db.query(Balance).filter(Balance.account_id == account_id).first()
        if balance:
            balance.ledger_balance += amount
            balance.available_balance += amount
    
    def _send_transaction_notifications(self, transaction: Transaction):
        """Send notifications for completed transactions"""
        try:
            from app.services.notification import NotificationService
            notification_service = NotificationService(self.db)
            
            # Notify sender
            if transaction.from_account_id:
                account = self.db.query(Account).filter(Account.id == transaction.from_account_id).first()
                if account and account.customer_id:
                    notification_service.send_transaction_notification(
                        account.customer_id, 
                        float(transaction.amount), 
                        "debited"
                    )
            
            # Notify receiver
            if transaction.to_account_id:
                account = self.db.query(Account).filter(Account.id == transaction.to_account_id).first()
                if account and account.customer_id:
                    notification_service.send_transaction_notification(
                        account.customer_id, 
                        float(transaction.amount), 
                        "credited"
                    )
        except Exception as e:
            # Don't fail transaction if notification fails
            print(f"Notification failed: {e}")