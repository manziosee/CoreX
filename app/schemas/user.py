from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from app.models.user import UserRole, UserStatus
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(UserBase):
    id: str
    status: UserStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class PasswordReset(BaseModel):
    username: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class UserStatusUpdate(BaseModel):
    status: UserStatus