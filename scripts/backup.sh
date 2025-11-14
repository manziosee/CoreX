#!/bin/bash
set -e

# Database backup script for production
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="coreX-DB"
DB_USER="postgres"
DB_HOST="postgres"

echo "🔄 Starting database backup at $(date)"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create PostgreSQL backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/corex_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/corex_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "corex_backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: corex_backup_$DATE.sql.gz"
echo "📊 Backup size: $(du -h $BACKUP_DIR/corex_backup_$DATE.sql.gz | cut -f1)"