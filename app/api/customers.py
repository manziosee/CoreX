from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer import CustomerService

router = APIRouter()

@router.post("/", response_model=CustomerResponse, summary="Create Customer", description="Register a new customer with KYC information")
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.create_customer(customer)

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