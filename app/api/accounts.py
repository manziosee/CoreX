from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.account import AccountCreate, AccountResponse, BalanceResponse
from app.services.account import AccountService

router = APIRouter()

@router.post("/", response_model=AccountResponse, summary="Create Account", description="Create a new bank account for a customer")
async def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    service = AccountService(db)
    return service.create_account(account)

@router.get("/{account_id}", response_model=AccountResponse, summary="Get Account", description="Retrieve account details by ID")
async def get_account(account_id: str, db: Session = Depends(get_db)):
    service = AccountService(db)
    account = service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/{account_id}/balance", response_model=BalanceResponse, summary="Get Balance", description="Get current account balance")
async def get_balance(account_id: str, db: Session = Depends(get_db)):
    service = AccountService(db)
    balance = service.get_balance(account_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance

@router.get("/customer/{customer_id}", response_model=List[AccountResponse], summary="Get Customer Accounts", description="Get all accounts for a specific customer")
async def get_customer_accounts(customer_id: str, db: Session = Depends(get_db)):
    service = AccountService(db)
    return service.get_customer_accounts(customer_id)