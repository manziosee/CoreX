#!/bin/bash
set -e

echo "🏦 Starting CoreX Banking System v1.0.0..."
echo "📅 $(date)"
echo "🌍 Environment: ${ENVIRONMENT:-production}"

# Set default environment variables
export DATABASE_URL="${DATABASE_URL:-sqlite:///app/data/corex.db}"
export ENVIRONMENT="${ENVIRONMENT:-production}"
export JWT_SECRET="${JWT_SECRET:-fly-production-secret-key-2024}"
export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-60}"

# Create necessary directories with proper permissions
echo "📁 Creating directories..."
mkdir -p /app/data /app/uploads /app/logs
chmod 755 /app/data /app/uploads /app/logs
touch /app/data/corex.db
chmod 644 /app/data/corex.db

# Initialize database
echo "📊 Initializing database..."
python3 -c "
import os
import sys
import sqlite3
try:
    # Ensure database file exists and is writable
    db_path = '/app/data/corex.db'
    if not os.path.exists(db_path):
        open(db_path, 'a').close()
    os.chmod(db_path, 0o644)
    
    # Test SQLite connection
    conn = sqlite3.connect(db_path)
    conn.execute('SELECT 1')
    conn.close()
    
    # Initialize with SQLAlchemy
    os.environ['DATABASE_URL'] = 'sqlite:///app/data/corex.db'
    from app.database import engine
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Create admin user if not exists
echo "👤 Setting up admin user..."
python3 -c "
import os
os.environ['DATABASE_URL'] = '${DATABASE_URL}'
try:
    from app.database import SessionLocal
    from app.models.user import User, UserRole, UserStatus
    from app.services.auth import get_password_hash
    import uuid
    
    db = SessionLocal()
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            username='admin',
            email='admin@corex-banking.com',
            password_hash=get_password_hash('admin123'),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        db.add(admin)
        db.commit()
        print('✅ Admin user created')
    else:
        print('✅ Admin user exists')
    db.close()
except Exception as e:
    print(f'⚠️  Admin user setup warning: {e}')
"

# Health check
echo "🔍 Running pre-flight checks..."
python3 -c "
try:
    from app.main import app
    print('✅ Application imports successful')
except Exception as e:
    print(f'❌ Application check failed: {e}')
    exit(1)
"

echo "🚀 Starting API server on port ${PORT:-8000}..."
echo "📚 API Documentation: https://corex-banking.fly.dev/docs"
echo "🔗 Health Check: https://corex-banking.fly.dev/health"

# Start the application with production settings
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --access-log \
    --log-level info \
    --no-use-colors