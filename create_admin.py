#!/usr/bin/env python3
"""
Create Admin User Script for CoreX Banking System
"""

import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User, UserRole, UserStatus
from app.services.auth import get_password_hash, get_user_by_username
import uuid

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = get_user_by_username(db, "admin")
        if existing_admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        password = "admin123"[:72]  # Truncate to 72 bytes for bcrypt
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@corex-banking.com",
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@corex-banking.com")
        print("   Role: ADMIN")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()