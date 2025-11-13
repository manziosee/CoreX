import pytest
from fastapi.testclient import TestClient
from app.main import app
import tempfile
import os

client = TestClient(app)

def test_customer_onboarding():
    """Test enhanced customer onboarding with additional fields"""
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "New York",
        "country": "USA",
        "occupation": "Software Engineer",
        "income_range": "50000-75000"
    }
    
    response = client.post("/customers/onboard", json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["kyc_status"] == "PENDING"
    assert data["city"] == "New York"

def test_get_pending_kyc_customers():
    """Test retrieving customers with pending KYC"""
    response = client.get("/customers/pending-kyc")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_kyc_document_types():
    """Test KYC document type validation"""
    from app.models.kyc import DocumentType
    assert DocumentType.NATIONAL_ID in DocumentType
    assert DocumentType.PASSPORT in DocumentType
    assert DocumentType.UTILITY_BILL in DocumentType

def test_kyc_workflow_requirements():
    """Test KYC workflow requirements"""
    from app.services.kyc_workflow import KYCWorkflowService
    from app.database import SessionLocal
    
    db = SessionLocal()
    workflow_service = KYCWorkflowService(db)
    requirements = workflow_service.get_kyc_requirements()
    
    assert "individual" in requirements
    assert "NATIONAL_ID" in requirements["individual"]
    assert "UTILITY_BILL" in requirements["individual"]
    db.close()

def test_customer_kyc_status_update():
    """Test KYC status update functionality"""
    # First create a customer
    customer_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com"
    }
    
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    customer_id = response.json()["id"]
    
    # Update KYC status
    status_update = {
        "kyc_status": "APPROVED",
        "reason": "All documents verified"
    }
    
    response = client.put(f"/customers/{customer_id}/kyc-status", json=status_update)
    assert response.status_code == 200
    assert response.json()["kyc_status"] == "APPROVED"