from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate
from app.core.config import settings
import uuid
import hashlib

# Use simple bcrypt context
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except:
    # Fallback to SHA256 if bcrypt fails
    pwd_context = None

def verify_password(plain_password, hashed_password):
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            pass
    # Fallback to SHA256
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    if pwd_context:
        try:
            return pwd_context.hash(password[:72])  # Truncate for bcrypt
        except:
            pass
    # Fallback to SHA256
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.status != UserStatus.ACTIVE:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = get_password_hash(user_data.password)
    user = User(
        id=uuid.uuid4(),
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def change_password(db: Session, username: str, current_password: str, new_password: str) -> bool:
    user = get_user_by_username(db, username)
    if not user or not verify_password(current_password, user.password_hash):
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return True

def reset_password(db: Session, username: str, new_password: str) -> bool:
    user = get_user_by_username(db, username)
    if not user:
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return True

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None