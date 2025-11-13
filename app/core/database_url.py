import os
from app.core.config import settings

def get_database_url():
    """Get database URL from environment or settings"""
    # Fly.io automatically sets DATABASE_URL for attached Postgres
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Convert postgres:// to postgresql:// for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    return settings.database_url