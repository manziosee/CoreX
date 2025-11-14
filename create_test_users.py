#!/usr/bin/env python3
"""
Create Test Users Script for CoreX Banking System
Creates users for all roles to test the system
"""

import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.services.auth import get_password_hash, get_user_by_username
import uuid

def create_test_users():
    """Create test users for all roles"""
    db = SessionLocal()
    
    test_users = [
        {
            "username": "admin",
            "email": "admin@corex-banking.com",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "teller1",
            "email": "teller1@corex-banking.com", 
            "password": "teller123",
            "role": UserRole.TELLER
        },
        {
            "username": "auditor1",
            "email": "auditor1@corex-banking.com",
            "password": "auditor123", 
            "role": UserRole.AUDITOR
        },
        {
            "username": "api_user1",
            "email": "api@corex-banking.com",
            "password": "api123",
            "role": UserRole.API_USER
        }
    ]
    
    try:
        created_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = get_user_by_username(db, user_data["username"])
            if existing_user:
                print(f"✅ User '{user_data['username']}' already exists")
                continue
            
            # Create new user
            user = User(
                id=uuid.uuid4(),
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
                status=UserStatus.ACTIVE
            )
            
            db.add(user)
            created_count += 1
            print(f"✅ Created user '{user_data['username']}' with role {user_data['role'].value}")
        
        db.commit()
        
        print(f"\n🎉 Test users setup complete!")
        print(f"   Created: {created_count} new users")
        print(f"   Total users available for testing:")
        
        for user_data in test_users:
            print(f"   - Username: {user_data['username']:<10} | Password: {user_data['password']:<10} | Role: {user_data['role'].value}")
        
        print(f"\n📚 Usage:")
        print(f"   1. Use any of these credentials to login via /auth/token")
        print(f"   2. Copy the access_token from response")
        print(f"   3. Use 'Bearer <token>' in Authorization header")
        print(f"   4. Test different endpoints based on user role permissions")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()