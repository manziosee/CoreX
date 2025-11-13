from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate
from typing import List, Optional
import uuid

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        # Generate customer number
        customer_number = f"CX{str(uuid.uuid4().int)[:8]}"
        
        customer = Customer(
            customer_number=customer_number,
            **customer_data.dict()
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_customer_by_number(self, customer_number: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_number == customer_number).first()
    
    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()
    
    def update_customer(self, customer_id: str, customer_data: dict) -> Optional[Customer]:
        customer = self.get_customer(customer_id)
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer