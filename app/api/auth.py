from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import Token, UserCreate, UserResponse, PasswordChange, PasswordReset
from app.services.auth import (
    authenticate_user, create_access_token, create_user, 
    change_password, reset_password, get_user_by_username
)
from app.core.auth import get_current_user, get_current_active_user, require_role
from datetime import timedelta
from app.core.config import settings
from typing import List

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=Token, summary="Login", description="Authenticate user and get access token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse, summary="Register User", description="Create new user account (Admin only)")
async def register_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = create_user(db, user_data)
    return user

@router.get("/me", response_model=UserResponse, summary="Current User", description="Get current user profile")
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/change-password", summary="Change Password", description="Change current user password")
async def change_user_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not change_password(db, current_user.username, password_data.current_password, password_data.new_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
    return {"message": "Password changed successfully"}

@router.post("/reset-password", summary="Reset Password", description="Reset user password (Admin only)")
async def reset_user_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    if not reset_password(db, reset_data.username, reset_data.new_password):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset successfully"}

@router.get("/users", response_model=List[UserResponse], summary="List Users", description="Get all users (Admin only)")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{username}/status", summary="Update User Status", description="Activate/Deactivate user (Admin only)")
async def update_user_status(
    username: str,
    status: UserStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.status = status
    db.commit()
    return {"message": f"User status updated to {status.value}"}

@router.delete("/logout", summary="Logout", description="Logout current user")
async def logout(current_user: User = Depends(get_current_user)):
    # In a real implementation, you might want to blacklist the token
    return {"message": "Successfully logged out"}