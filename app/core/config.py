from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:2001@localhost:5432/coreX-DB")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # RabbitMQ Configuration
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # JWT Configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = int(os.getenv("RATE_LIMIT_RPM", "60"))
    
    # Security
    password_min_length: int = 8
    max_login_attempts: int = 5
    account_lockout_duration: int = 30  # minutes
    
    class Config:
        env_file = ".env"

settings = Settings()