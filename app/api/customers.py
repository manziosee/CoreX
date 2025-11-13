from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerOnboarding, KYCStatusUpdate
from app.services.customer import CustomerService

router = APIRouter()

@router.post("/", response_model=CustomerResponse, summary="Create Customer", description="Register a new customer with KYC information")
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.create_customer(customer)

@router.post("/onboard", response_model=CustomerResponse, summary="Onboard Customer", description="Enhanced customer onboarding with additional information")
async def onboard_customer(customer: CustomerOnboarding, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.onboard_customer(customer)

@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get Customer", description="Retrieve customer details by ID")
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/", response_model=List[CustomerResponse], summary="List Customers", description="Get paginated list of all customers")
async def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.list_customers(skip=skip, limit=limit)

@router.put("/{customer_id}/kyc-status", response_model=CustomerResponse, summary="Update KYC Status", description="Update customer KYC verification status")
async def update_kyc_status(customer_id: str, status_update: KYCStatusUpdate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.update_kyc_status(customer_id, status_update)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/pending-kyc", response_model=List[CustomerResponse], summary="Pending KYC Customers", description="Get customers with pending KYC verification")
async def get_pending_kyc_customers(db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.get_pending_kyc_customers()