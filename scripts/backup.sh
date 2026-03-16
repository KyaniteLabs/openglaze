#!/bin/bash
# Glaze Lab Backup Script
# Creates a backup of the database and uploaded files

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="glazelab_backup_${DATE}"

echo "================================================"
echo "  Glaze Lab Backup"
echo "================================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if running with Docker
if docker-compose ps | grep -q postgres; then
    echo "Backing up PostgreSQL database..."

    # Get database credentials from environment
    DB_HOST="postgres"
    DB_USER="glazelab"
    DB_NAME="glazelab"

    # Create database backup
    docker-compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/${BACKUP_NAME}_database.sql"
    echo "  ✓ Database backed up to ${BACKUP_NAME}_database.sql"
else
    echo "Backing up SQLite database..."

    if [ -f "glazelab.db" ]; then
        cp glazelab.db "$BACKUP_DIR/${BACKUP_NAME}_database.db"
        echo "  ✓ Database backed up to ${BACKUP_NAME}_database.db"
    else
        echo "  ✗ No database file found"
    fi
fi

# Backup uploaded files (if any)
if [ -d "uploads" ]; then
    echo "Backing up uploaded files..."
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz" uploads/
    echo "  ✓ Uploads backed up to ${BACKUP_NAME}_uploads.tar.gz"
fi

# Backup configuration
if [ -f ".env" ]; then
    echo "Backing up configuration..."
    # Exclude sensitive keys from backup
    grep -v "KEY\|SECRET\|PASSWORD" .env > "$BACKUP_DIR/${BACKUP_NAME}_config.env"
    echo "  ✓ Configuration backed up to ${BACKUP_NAME}_config.env"
fi

# Create compressed archive
echo ""
echo "Creating backup archive..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" -C "$BACKUP_DIR" \
    ${BACKUP_NAME}_database.sql 2>/dev/null || \
    ${BACKUP_NAME}_database.db 2>/dev/null || true

if [ -f "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz" ]; then
    tar -rf "$BACKUP_DIR/${BACKUP_NAME}.tar" -C "$BACKUP_DIR" ${BACKUP_NAME}_uploads.tar.gz
fi

# Compress final archive
gzip -f "$BACKUP_DIR/${BACKUP_NAME}.tar" 2>/dev/null || true

echo "  ✓ Full backup: ${BACKUP_NAME}.tar.gz"

# Clean up intermediate files
rm -f "$BACKUP_DIR/${BACKUP_NAME}_database.sql" 2>/dev/null || true
rm -f "$BACKUP_DIR/${BACKUP_NAME}_database.db" 2>/dev/null || true
rm -f "$BACKUP_DIR/${BACKUP_NAME}_uploads.tar.gz" 2>/dev/null || true
rm -f "$BACKUP_DIR/${BACKUP_NAME}_config.env" 2>/dev/null || true

# Show backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)
echo ""
echo "Backup size: $BACKUP_SIZE"
echo "Backup location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# Retention policy - keep last 7 daily backups
echo ""
echo "Applying retention policy (keeping last 7 backups)..."
ls -t "$BACKUP_DIR"/glazelab_backup_*.tar.gz | tail -n +8 | xargs -r rm
echo "  ✓ Old backups cleaned up"

echo ""
echo "================================================"
echo "  Backup Complete!"
echo "================================================"
