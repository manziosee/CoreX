import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.services.auth import create_user, get_password_hash
from app.schemas.user import UserCreate
import uuid

client = TestClient(app)

def test_login_success(test_db: Session):
    """Test successful login"""
    # Create test user
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role=UserRole.TELLER
    )
    create_user(test_db, user_data)
    
    # Test login
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/token",
        data={"username": "invalid", "password": "invalid"}
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_register_user_admin_only(test_db: Session):
    """Test user registration requires admin role"""
    # Create admin user
    admin_data = UserCreate(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role=UserRole.ADMIN
    )
    admin_user = create_user(test_db, admin_data)
    
    # Login as admin
    login_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Register new user
    new_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass123",
        "role": "TELLER"
    }
    
    response = client.post(
        "/auth/register",
        json=new_user_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "TELLER"

def test_get_current_user(test_db: Session):
    """Test getting current user profile"""
    # Create and login user
    user_data = UserCreate(
        username="profileuser",
        email="profile@example.com",
        password="profile123",
        role=UserRole.TELLER
    )
    create_user(test_db, user_data)
    
    login_response = client.post(
        "/auth/token",
        data={"username": "profileuser", "password": "profile123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profileuser"
    assert data["email"] == "profile@example.com"

def test_change_password(test_db: Session):
    """Test password change"""
    # Create and login user
    user_data = UserCreate(
        username="changepass",
        email="changepass@example.com",
        password="oldpass123",
        role=UserRole.TELLER
    )
    create_user(test_db, user_data)
    
    login_response = client.post(
        "/auth/token",
        data={"username": "changepass", "password": "oldpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.put(
        "/auth/change-password",
        json={
            "current_password": "oldpass123",
            "new_password": "newpass123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "Password changed successfully" in response.json()["message"]

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_role_based_access(test_db: Session):
    """Test role-based access control"""
    # Create teller user
    teller_data = UserCreate(
        username="teller",
        email="teller@example.com",
        password="teller123",
        role=UserRole.TELLER
    )
    create_user(test_db, teller_data)
    
    # Login as teller
    login_response = client.post(
        "/auth/token",
        data={"username": "teller", "password": "teller123"}
    )
    token = login_response.json()["access_token"]
    
    # Try to access admin-only endpoint
    response = client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]