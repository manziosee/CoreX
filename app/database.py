from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Handle different database URLs for different environments
database_url = settings.database_url

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# For SQLite in production (Fly.io simple deployment)
if database_url.startswith("sqlite://"):
    # Ensure directory exists for SQLite
    os.makedirs("/app/data", exist_ok=True)
    if database_url == "sqlite:///app/corex.db":
        database_url = "sqlite:///app/data/corex.db"

engine = create_engine(database_url, 
                     connect_args={"check_same_thread": False} if "sqlite" in database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()