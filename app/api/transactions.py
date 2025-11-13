from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction import TransactionService

router = APIRouter()

@router.post("/", response_model=TransactionResponse, summary="Create Transaction", description="Create a new banking transaction (deposit, withdrawal, transfer)")
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.create_transaction(transaction)

@router.get("/{transaction_id}", response_model=TransactionResponse, summary="Get Transaction", description="Retrieve transaction details by ID")
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/account/{account_id}", response_model=List[TransactionResponse], summary="Get Account Transactions", description="Get paginated transaction history for an account")
async def get_account_transactions(account_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_account_transactions(account_id, skip=skip, limit=limit)

@router.post("/{transaction_id}/process", summary="Process Transaction", description="Process a pending transaction using double-entry accounting")
async def process_transaction(transaction_id: str, db: Session = Depends(get_db)):
    service = TransactionService(db)
    result = service.process_transaction(transaction_id)
    if not result:
        raise HTTPException(status_code=400, detail="Transaction processing failed")
    return {"message": "Transaction processed successfully"}