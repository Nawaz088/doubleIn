#!/bin/bash
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/doublehq_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-doublehq} | gzip > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "doublehq_*.sql.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
