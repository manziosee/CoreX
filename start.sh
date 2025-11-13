#!/bin/bash
set -e

echo "🏦 Starting CoreX Banking System..."

# Set environment variables
export DATABASE_URL="sqlite:///app/data/corex.db"
export ENVIRONMENT="production"

# Create data directory
mkdir -p /app/data

# Initialize database
echo "📊 Initializing database..."
python3 -c "
import os
os.environ['DATABASE_URL'] = 'sqlite:///app/data/corex.db'
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized successfully')
"

# Start the application
echo "🚀 Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000